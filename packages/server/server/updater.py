import chromadb
from server.file_utilities import get_files_to_process, handle_file

# Init a Chroma client
chroma_client = chromadb.HttpClient(host='localhost', port=8000)
collection = chroma_client.get_or_create_collection('repo-chat')

number_of_docs = collection.count()
print('Number of documents in collection:', number_of_docs)

directory_path = './../'
codebase = get_files_to_process(directory_path)

file_results = [handle_file(file) for file in codebase['files']]
for result in file_results:
    print(result['id'], result['filepath'])

ids = [result['id'] for result in file_results]

# Make sure the ids are unique
unique_ids = set(ids)
non_unique_ids = set([id for id in ids if ids.count(id) > 1])
if len(non_unique_ids) > 0:
    print('Non-unique ids:', non_unique_ids)
    # print the paths of the files with non-unique ids
    for id in non_unique_ids:
        print('Files with id:', id)
        for result in file_results:
            if result['id'] == id:
                print(result['filepath'])
        print()

assert len(ids) == len(set(ids)), 'The ids are not unique'

docs = [result['content'] for result in file_results]
collection.upsert(ids, documents=docs)

print("Added", len(docs), "docs to collection")
count_final = collection.count()
log = f"Collection {collection.name}, {abs(number_of_docs - count_final)} documents {
    'removed' if number_of_docs - count_final < 0 else 'added'}\n\n"

# Remove docs that are no longer in the repo
all_ids = collection.peek(limit=1000)['ids']
ids_to_remove = [id for id in all_ids if id not in ids]
log += f"Removing {len(ids_to_remove)} documents\n\n"
collection.delete(ids=ids_to_remove)
log += f"Collection {collection.name}, {collection.count()} documents\n\n"

print(log)
