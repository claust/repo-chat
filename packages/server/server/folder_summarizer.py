import os

from langchain_ollama import ChatOllama
from server.file_utilities import FileResult, get_files_to_process, read_file_content
from server.repositories.documentation_repo import DocumentationRepository, FolderDocumentation


class FolderSummarizer:
    def __init__(self) -> None:
        self.llm = ChatOllama(model="llama3.2", num_ctx=5000)

    def document_code(self) -> str:
        documentation_repo = DocumentationRepository()

        number_of_docs = documentation_repo.count()
        print(f'{number_of_docs} documents documented')

        base_folder = os.getenv('BASE_FOLDER') or './../../'
        codebase = get_files_to_process(base_folder)

        stored_ids = documentation_repo.query_all_ids_of_type(
            FolderDocumentation())

        # WIP
        file_results = [result for result in (read_file_content(
            base_folder, file, skip_content=True) for file in codebase["files"])]
        repo_ids = [result["id"] for result in file_results]
        new_file_results = [
            result for result in file_results if result["id"] not in stored_ids]
        removed_ids = [id for id in stored_ids if id not in repo_ids]

        # Document the new files
        for index, result in enumerate(new_file_results):
            print(index, result["id"], result["relative_file_path"])
            result = read_file_content(base_folder, result["file_path"])
            summary = self.prepare_summary(result)
            print(summary[:50])
            summary = result["relative_file_path"] + "\n" + summary
            documentation_repo.upsert([result["id"]], [summary])

        # Remove docs that are no longer in the repo
        if len(removed_ids) > 0:
            print(f"Removing {len(removed_ids)} documents\n\n")
            documentation_repo.remove_docs(ids=removed_ids)
            print("Removed", len(removed_ids), "docs from collection")

        count_final = documentation_repo.count()
        log = f"Collection {documentation_repo.name()} contains {count_final} documents, {abs(number_of_docs - count_final)} {
            'added' if number_of_docs - count_final <= 0 else 'removed'}\n\n"
        print(log)
        return log

    def prepare_summary(self, file_result: FileResult) -> str:
        messages = [
            ("system", """You are an expert programmer specialised in writing excellent documentation of source code and configuration files.
                You will read the following source code or configuration and write a summary of the purpose of the code, including any important details.
                You will end the summary with a comma separated list of the most important keywords that are directly relevant to the code.
                You will respond simply with the summary of the code. Do not include any of the code in your response.
                Do not include any conversational elements in your response, like "It appears that you have provided ...".
                Just respond with the summary and keywords.
                """),
            ("user", f"<file_name>{
             file_result["relative_file_path"]}</file_name><content>{file_result["content"]}</content><documentation>")
        ]
        response = self.llm.invoke(messages, {})
        return response.content


if __name__ == '__main__':
    FolderSummarizer().document_code()
