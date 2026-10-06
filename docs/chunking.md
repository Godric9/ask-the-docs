# Chunking

This document describes the chunking process used in the `ask-the-docs` project. Chunking is a technique used to break down large documents into smaller, more manageable pieces, or "chunks," which can then be processed individually. This is particularly useful for tasks such as semantic search, where understanding the context of a document is crucial.

In this project, we implemented three different chunking strategies: fixed-size chunking, recursive chunking, and semantic chunking. Each strategy has its own advantages and use cases, which are described below.

## Fixed-Size Chunking
Fixed-size chunking involves splitting a document into chunks of a predetermined size. This method is straightforward and easy to implement, but it may not always capture the semantic meaning of the text effectively. It is best suited for documents where the content is relatively uniform and does not require deep understanding.

## Recursive Chunking
Recursive chunking is a more sophisticated approach that involves breaking down a document into smaller chunks based on its structure, such as paragraphs or sections. This method allows for a more natural division of the text, preserving the context and meaning of the content. Recursive chunking is particularly useful for documents with a clear hierarchical structure, such as technical manuals or academic papers. But it can lead to chunks that cut off in the middle of a sentence, which can be problematic for semantic understanding.

## Semantic Chunking
Semantic chunking is the most advanced chunking strategy, which involves analyzing the semantic content of the document to create chunks that are meaningful and contextually relevant. This method uses natural language processing techniques to identify the boundaries of chunks based on the semantic relationships between sentences and paragraphs. Semantic chunking is ideal for documents where understanding the context and meaning of the text is crucial. But it can also lead to chunks that do not align with the questions being asked because the chunks that are short and semantically similar may not contain the information needed to answer a specific question and will be at the top of the search results.

## Conclusion
In summary, the choice of chunking strategy depends on the specific requirements of the task at hand.

Here we have documents that are docs from the Datadog documentation. The documents are in markdown format and contain a lot of code snippets. The documents are also quite long, so we need to chunk them into smaller pieces for processing.

On some tests the recursive chunking strategy was found to be the best for this type of document, as it preserves the context and meaning of the content. However, in some cases, semantic chunking may be more appropriate, especially when dealing with documents that require a deeper understanding of the text.

We will continue with the recursive chunking strategy for now, but we may explore semantic chunking in the future if we find that it provides better results for our specific use case.