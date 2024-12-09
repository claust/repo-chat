import os
from server.code_repo import CodeRepository
from server.file_utilities import get_files_to_process, read_file_content


def document_code() -> str:
    code_repo = CodeRepository()

    number_of_docs = code_repo.count()
    print(f'{number_of_docs} documents indexed')

    base_folder = os.getenv('BASE_FOLDER') or './../../'
    codebase = get_files_to_process(base_folder)

    file_results = [result for result in (read_file_content(
        base_folder, file) for file in codebase["files"])]
    for result in file_results[:20]:
        print(result["id"], result["relative_file_path"])

    stored_ids = code_repo.get_all_ids()
    repo_ids = [result["id"] for result in file_results]
    new_file_results = [
        result for result in file_results if result["id"] not in stored_ids]
    new_ids = [result["id"] for result in new_file_results]
    new_docs = [result["content"] for result in new_file_results]
    removed_ids = [id for id in stored_ids if id not in repo_ids]

    # Make sure the ids are unique
    unique_ids = set(new_ids)
    non_unique_ids = set([id for id in new_ids if new_ids.count(id) > 1])
    if len(non_unique_ids) > 0:
        print('Non-unique ids:', non_unique_ids)
        # print the paths of the files with non-unique ids
        for id in non_unique_ids:
            print('Files with id:', id)
            for result in file_results:
                if result["id"] == id:
                    print(result["relative_file_path"])
            print()

    assert len(new_ids) == len(set(new_ids)), 'The ids are not unique'

    if len(new_ids) > 0:
        print(f"Adding {len(new_ids)} new documents\n\n")
        batch_size = 100
        for i in range(0, len(new_ids), batch_size):
            print(f"Adding {i} to {i + batch_size} documents")
            code_repo.upsert(new_ids[i:i + batch_size],
                             new_docs[i:i + batch_size])
        print("Added", len(new_docs), "docs to collection")
    # Remove docs that are no longer in the repo
    if len(removed_ids) > 0:
        print(f"Removing {len(removed_ids)} documents\n\n")
        code_repo.remove_docs(ids=removed_ids)
        print("Removed", len(removed_ids), "docs from collection")

    count_final = code_repo.count()
    log = f"Collection {code_repo.name()} contains {count_final} documents, {abs(number_of_docs - count_final)} {
        'added' if number_of_docs - count_final <= 0 else 'removed'}\n\n"
    print(log)
    return log
