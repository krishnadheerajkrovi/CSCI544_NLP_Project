import lucene

from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, StringField, TextField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, DirectoryReader
from org.apache.lucene.search import IndexSearcher,ScoreDoc, TopDocs
from org.apache.lucene.queries.mlt import MoreLikeThisQuery
from org.apache.lucene.store import NIOFSDirectory
from org.apache.lucene.util import Version
from java.nio.file import Paths
import os
from argparse import ArgumentParser


def create_index():
    try:
        index_dir = '/Project/data/indexdir'
        directory = NIOFSDirectory(Paths.get(index_dir))
        # Indexing
        analyzer = StandardAnalyzer()
        config = IndexWriterConfig(analyzer)
        if not os.path.exists(index_dir):
            print('Created dir')
            os.mkdir(index_dir)
        #     config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        # else:
        #     config.setOpenMode()
        writer = IndexWriter(directory, config)

        # create documents
        doc1 = Document()
        doc1.add(Field("content", "The quick brown fox jumped over the lazy dog",  TextField.TYPE_STORED))
        writer.addDocument(doc1)

        doc2 = Document()
        doc2.add(Field("content", "The quick brown fox leaped over the dog",  TextField.TYPE_STORED))
        writer.addDocument(doc2)

        doc3 = Document()
        doc3.add(Field("content", "The quick brown rabbit jumped over the lazy dog",  TextField.TYPE_STORED))
        writer.addDocument(doc3)
    except Exception as e:
        print(e)
    finally:
        writer.commit()
        writer.close()
        directory.close()


def search_index():
    try:
        index_dir = '/Project/data/indexdir'
        directory = NIOFSDirectory(Paths.get(index_dir))
        # Searching
        searcher = IndexSearcher(DirectoryReader.open(directory))
        analyzer = StandardAnalyzer()
        # Get MoreLikeThisQuery for the first document
        # more_like_this = MoreLikeThisQuery("dude my employer uses svb we are dead in the water right now",["content"],analyzer,'content')
        more_like_this = MoreLikeThisQuery("The quick brown fox jumped over the dog",["content"],analyzer,'content')
        hits = searcher.search(more_like_this,10).scoreDocs
        print(hits)
        # print results
        print(f"Found {len(hits)} hits:")
        for hit in hits:
            doc = searcher.doc(hit.doc)
            print(f"  {doc['content']} (score: {hit.score})")
        # Search using MoreLikeThisQuery and calculate cosine similarity
        # top_docs = searcher.search(more_like_this, 10)
        # for hit in top_docs.scoreDocs:
        #     doc = searcher.doc(hit.doc)
        #     score = hit.score
        #     print(f"Score: {score} | Content: {doc.get('content')}")
    finally:
        del searcher
        directory.close()

if __name__ == "__main__":
    lucene.initVM()
    parser = ArgumentParser()
    parser.add_argument("--mode", "-m", type=str, choices=['create', 'search'], default='create')
    args = parser.parse_args()
    if args.mode == 'create':
        create_index()
    elif args.mode == 'search':
        search_index()