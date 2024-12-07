from server.code_repo import CodeRepository
from server.file_utilities import get_files_to_process, handle_file

code_repo = CodeRepository()

number_of_docs = code_repo.count()
print('Number of documents in collection:', number_of_docs)

base_folder = './../../'
codebase = get_files_to_process(base_folder)

file_results = [result for result in (handle_file(
    base_folder, file) for file in codebase.files)]
for result in file_results:
    print(result.id, result.relative_file_path)

ids = [result.id for result in file_results]

# Make sure the ids are unique
unique_ids = set(ids)
non_unique_ids = set([id for id in ids if ids.count(id) > 1])
if len(non_unique_ids) > 0:
    print('Non-unique ids:', non_unique_ids)
    # print the paths of the files with non-unique ids
    for id in non_unique_ids:
        print('Files with id:', id)
        for result in file_results:
            if result.id == id:
                print(result.relative_file_path)
        print()

assert len(ids) == len(set(ids)), 'The ids are not unique'

docs = [result.content for result in file_results]
code_repo.upsert(ids, docs)

print("Added", len(docs), "docs to collection")
count_final = code_repo.count()
log = f"Collection {code_repo.name()}, {abs(number_of_docs - count_final)} documents {
    'removed' if number_of_docs - count_final < 0 else 'added'}\n\n"

# Remove docs that are no longer in the repo
all_ids = code_repo.get_all_ids()
ids_to_remove = [id for id in all_ids if id not in ids]
if len(ids_to_remove) > 0:
    log += f"Removing {len(ids_to_remove)} documents\n\n"
    code_repo.remove_docs(ids=ids_to_remove)

log += f"Collection {code_repo.name()}, {code_repo.count()} documents\n\n"

print(log)
