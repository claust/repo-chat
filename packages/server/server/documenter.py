import os

from chromadb import HttpClient
from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI
from server.base_repo import BaseRepository
from server.code_repo import CodeRepository
from server.file_utilities import FileResult, get_files_to_process, read_file_content


class SourceCodeDocumenter:
    def __init__(self) -> None:
        self.llm = ChatOllama(model="llama3.2")

    def document_code(self) -> str:
        http_client = HttpClient(host="localhost", port=8000)
        documentation_repo = BaseRepository(
            collection="documentation", http_client=http_client)

        number_of_docs = documentation_repo.count()
        print(f'{number_of_docs} documents documented')

        base_folder = os.getenv('BASE_FOLDER') or './../../'
        codebase = get_files_to_process(base_folder)

        file_results = [result for result in (read_file_content(
            base_folder, file) for file in codebase["files"])]
        for index, result in enumerate(file_results):
            print(index, result["id"], result["relative_file_path"])
            summary = self.prepare_summary(result)
            print(summary[:50])
            summary = result["relative_file_path"] + "\n" + summary
            documentation_repo.upsert([result["id"]], [summary])

        count_final = documentation_repo.count()
        log = f"Collection {documentation_repo.name()} contains {count_final} documents, {abs(number_of_docs - count_final)} {
            'added' if number_of_docs - count_final <= 0 else 'removed'}\n\n"
        print(log)
        return log

    def prepare_summary(self, file_result: FileResult) -> str:
        messages = [
            ("system", """You are an expert programmer specialised in writing excellent documentation of source code and configuration files.
                You will read the following source code or configuration and write a summary of the purpose of the code, including any important details.
                You will end the summary with a list of keywords that are directly relevant to the code.
                You will respond simply with the summary of the code. Do not include any of the code in your response.
                """),
            ("human", f"<file_name>{
             file_result["relative_file_path"]}</file_name><content>{file_result["content"]}</content>")
        ]
        response = self.llm.invoke(messages)
        return response.content


if __name__ == '__main__':
    SourceCodeDocumenter().document_code()
