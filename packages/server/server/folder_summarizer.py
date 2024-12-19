import hashlib
import os
from typing import List

from langchain_ollama import ChatOllama
from server.file_utilities import FileResult, FolderResult, get_files_to_process, read_file_content
from server.repositories import DocumentationRepository, FolderDocumentation


class FolderSummarizer:
    def __init__(self) -> None:
        self.llm = ChatOllama(model="llama3.2", num_ctx=5000)
        self.documentation_repo = DocumentationRepository()

    def document_code(self) -> str:

        number_of_docs = self.documentation_repo.count()
        print(f'{number_of_docs} documents documented')

        base_folder = os.getenv('BASE_FOLDER') or './../../'
        codebase = get_files_to_process(base_folder)

        stored_ids = self.documentation_repo.query_all_ids_of_type(
            FolderDocumentation())

        folders = codebase["folders"]
        folder_results: List[FolderResult] = []
        for folder in folders:
            path_prefix = folder + os.sep
            files_in_folder = [file for file in codebase["files"]
                               if file.startswith(path_prefix) and file.count(os.sep, len(folder) + 1) == 0]
            file_results = [read_file_content(base_folder, file_path)
                            for file_path in files_in_folder]
            hashes = [result["id"] for result in file_results]
            folder_hash = hashlib.md5("".join(hashes).encode()).hexdigest()
            relative_folder_path = os.path.relpath(folder, base_folder)
            folder_depth = relative_folder_path.count(os.sep)
            folder_results.append({
                "folder_path": folder,
                "relative_folder_path": relative_folder_path,
                "folder_depth": folder_depth,
                "file_results": file_results,
                "id": folder_hash
            })

        folder_results = sorted(
            folder_results, key=lambda x: -x["folder_depth"])
        repo_ids = [result["id"] for result in folder_results]
        new_folder_results = [
            result for result in folder_results if result["id"] not in stored_ids]
        removed_ids = [id for id in stored_ids if id not in repo_ids]

        # Document the new or changed folders
        for index, result in enumerate(new_folder_results):
            print(index, result["id"], result["relative_folder_path"])
            file_summaries = self.read_file_summaries(result["file_results"])
            subfolder_summaries = self.read_subfolder_summaries(
                result["folder_path"])
            summary = self.prepare_summary(result,
                                           self.format_file_summaries(
                                               file_summaries),
                                           self.format_subfolder_summaries(subfolder_summaries) if len(subfolder_summaries) > 0 else None)
            print(summary[:50])
            summary = result["relative_folder_path"] + "\n" + summary
            self.documentation_repo.upsert(
                [result["id"]], [summary], {"folder_summary": True, "relative_folder_path": result["relative_folder_path"]})

        # Remove docs that are no longer in the repo
        if len(removed_ids) > 0:
            print(f"Removing {len(removed_ids)} documents\n\n")
            self.documentation_repo.remove_docs(ids=removed_ids)
            print("Removed", len(removed_ids), "docs from collection")

        count_final = self.documentation_repo.count()
        log = f"Collection {self.documentation_repo.name()} contains {count_final} documents, {abs(number_of_docs - count_final)} {
            'added' if number_of_docs - count_final <= 0 else 'removed'}\n\n"
        print(log)
        return log

    def read_file_summaries(self, file_results: List[FileResult]) -> List[str]:
        file_ids = [result["id"] for result in file_results]
        file_path = file_results[0]["file_path"]
        relative_folder = os.path.relpath(
            os.path.dirname(file_path), os.getenv('BASE_FOLDER') or './../../')
        summaries_with_file_paths = (
            self.documentation_repo.get_by_id(file_ids) or [])
        summaries_without_file_paths = [
            summary[len(relative_folder) + len(os.sep):] for summary in summaries_with_file_paths]
        return summaries_without_file_paths

    def read_subfolder_summaries(self, folder_path: str) -> List[str]:
        subfolders = [folder for folder in os.listdir(
            folder_path) if os.path.isdir(folder)]
        relative_folder_path = os.path.relpath(folder_path, os.getenv(
            'BASE_FOLDER') or './../../')
        subfolder_results: List[str] = []
        for subfolder in subfolders:
            subfolder_relative_path = os.path.join(
                relative_folder_path, subfolder)
            subfolder_summary = self.documentation_repo.search(
                query="", metadata={"relative_folder_path": subfolder_relative_path}) or []
            subfolder_results.extend(subfolder_summary)
        return subfolder_results

    def format_file_summaries(self, summaries: List[str]) -> str:
        return "Summary of file " + "\n\nSummary of file ".join(summaries)

    def format_subfolder_summaries(self, summaries: List[str]) -> str:
        return "Summary of folder " + "\n\nSummary of folder ".join(summaries)

    def prepare_summary(self, file_result: FolderResult, file_summaries: str | None, folder_summaries: str | None) -> str:
        messages = [
            ("system", f"""You are an expert programmer specialised in writing excellent documentation of source code and configuration files.
                You will summarize the purpose of the code in the folder/package: {file_result["relative_folder_path"]}
                The folder might contain source code or configuration and subfolders.
                You are provided with a list of summaries of the all the files and subfolders in the folder.
                You will end the summary with a comma separated list of the most important keywords that are directly relevant to the package.
                You will respond simply with the summary of the content of the folder. Do not include any of the code in your response.
                Do not include any conversational elements in your response, like "It appears that you have provided ...".
                Just respond with the summary and keywords.
                """),
            ("user", f"""How would you summarize the purpose of this package/folder?
                {"These are the existing file summaries: " +
                 file_summaries if file_summaries else ""}
                {"These are the existing subfolder summaries: " + folder_summaries if folder_summaries else ""}""")
        ]
        response = self.llm.invoke(messages, {})
        return response.content


if __name__ == '__main__':
    FolderSummarizer().document_code()
    os._exit(0)
