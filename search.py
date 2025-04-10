import os
import re
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser, MultifieldParser
import shutil
import logging


log = logging.getLogger("runbook-indexer")

class RunbookSearchEngine(object):

    def __init__(self, runbooks_dir: str, index_dir: str):
        self.__runbooks_dir = runbooks_dir
        self.__index_dir = index_dir

        self.__runbook_names = []

        # Define schema for our search index
        self.__schema = Schema(
            path=ID(stored=True),
            name=TEXT(stored=True),
            content=TEXT(stored=True)
        )

    @property
    def runbook_names(self):
        """Get the list of runbook names."""
        return self.__runbook_names

    def get_runbook_by_name(self, name: str) -> str:
        """Get the runbook by name."""
        for runbook in self.__runbook_names:
            if runbook == name:
                return runbook
        return ""

    def create_index(self):
        """Create or recreate the search index."""
        log.info(f"Creating search index at {self.__index_dir}")
        if os.path.exists(self.__index_dir):
            shutil.rmtree(self.__index_dir)

        os.mkdir(self.__index_dir)

        idx = create_in(self.__index_dir, self.__schema)
        writer = idx.writer()

        # Add runbook files to the index.
        for root_dir, _, files in os.walk(self.__runbooks_dir):
            for filename in files:
                if not filename.endswith((".md", ".txt")):
                    continue

                root, ext = os.path.splitext(filename)
                name = os.path.basename(root)

                self.__runbook_names.append(name)

                path = os.path.join(root_dir, filename)
                with open(path, "r", encoding="utf-8") as file:
                    content = file.read()

                    writer.add_document(
                        path=path,
                        name=name,
                        content=content
                    )
                    log.info(f"Added {filename} to the index")

        writer.commit()
        log.info(f"Indexing completed. {len(self.__runbook_names)} runbooks indexed.")
        return idx

    def __get_index(self):
        """Get the search index, creating it if necessary."""
        if not os.path.exists(self.__index_dir):
            return self.create_index()

        return open_dir(self.__index_dir)


    def search_runbooks(self, query_str: str, limit):
        """Search runbooks using Whoosh."""
        idx = self.__get_index()

        results = []
        with idx.searcher() as searcher:
            # Search both name and content, but give name higher weight
            query_parser = MultifieldParser(["name", "content"], idx.schema)
            query = query_parser.parse(query_str)

            search_results = searcher.search(query, limit=limit)
            search_results.fragmenter.maxchars = 200  # Length of context
            search_results.fragmenter.surround = 50   # Words surrounding matched term

            log.info("Found %d results for query: %s", len(search_results), query_str)
            for hit in search_results:
                highlight = hit.highlights("content")
                # If no highlight available, just take the first part of the content.
                if not highlight:
                    highlight = hit["content"][:250] + "..."

                results.append({
                    "name": hit["name"],
                    "path": hit["path"],
                    "snippet": highlight,
                    "score": hit.score
                })

        return results
