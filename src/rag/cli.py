"""CLI interface for the RAG Q&A system."""

import click

from .config import Settings
from .generation.generator import Generator
from .ingestion.pipeline import IngestionPipeline
from .retrieval.retriever import Retriever


@click.group()
def cli():
    """RAG Q&A System — Ask questions about your document collection."""
    pass


@cli.command()
@click.option("--dir", "documents_dir", default=None, help="Directory containing documents to ingest.")
def ingest(documents_dir: str | None):
    """Ingest documents into the vector store."""
    settings = Settings()
    if not settings.openai_api_key:
        click.echo(click.style("Error: OPENAI_API_KEY is not set. Copy .env.example to .env and add your key.", fg="red"))
        raise SystemExit(1)

    pipeline = IngestionPipeline(settings)

    from pathlib import Path
    directory = Path(documents_dir) if documents_dir else None

    click.echo("Ingesting documents...")
    stats = pipeline.ingest_all(directory)
    click.echo(click.style(f"Done! Ingested {stats['documents']} documents ({stats['chunks']} chunks).", fg="green"))


@cli.command()
@click.argument("question")
@click.option("-v", "--verbose", is_flag=True, help="Show retrieved chunks and scores.")
@click.option("-k", "--top-k", default=None, type=int, help="Number of chunks to retrieve.")
def ask(question: str, verbose: bool, top_k: int | None):
    """Ask a question about the ingested documents."""
    settings = Settings()
    if not settings.openai_api_key:
        click.echo(click.style("Error: OPENAI_API_KEY is not set. Copy .env.example to .env and add your key.", fg="red"))
        raise SystemExit(1)

    retriever = Retriever(settings)
    generator = Generator(settings)

    # Retrieve relevant chunks
    chunks = retriever.retrieve(question, top_k=top_k)

    if verbose:
        click.echo(click.style(f"\n--- Retrieved {len(chunks)} chunks ---", fg="cyan"))
        for i, chunk in enumerate(chunks, 1):
            click.echo(click.style(f"\n[{i}] {chunk.source} (score: {chunk.score:.3f})", fg="cyan"))
            click.echo(chunk.text[:200] + ("..." if len(chunk.text) > 200 else ""))
        click.echo(click.style("\n--- Generating answer ---\n", fg="cyan"))

    # Generate answer
    answer = generator.generate(question, chunks)

    if answer.is_supported:
        click.echo(click.style("\nAnswer:", fg="green", bold=True))
        click.echo(answer.text)
        click.echo(click.style("\nSources:", fg="cyan"))
        for source in answer.sources:
            click.echo(f"  - {source.document} (passage {source.passage_number}, score: {source.score})")
    else:
        click.echo(click.style("\nAnswer (not supported by documents):", fg="yellow", bold=True))
        click.echo(answer.text)


@cli.command(name="list")
def list_docs():
    """List all indexed documents."""
    settings = Settings()
    if not settings.openai_api_key:
        click.echo(click.style("Error: OPENAI_API_KEY is not set.", fg="red"))
        raise SystemExit(1)

    pipeline = IngestionPipeline(settings)
    docs = pipeline.list_documents()

    if not docs:
        click.echo("No documents indexed.")
        return

    click.echo(click.style(f"\nIndexed documents ({len(docs)}):", fg="green", bold=True))
    for doc in docs:
        click.echo(f"  - {doc['filename']} ({doc['type']}, {doc['chunks']} chunks)")


@cli.command()
@click.argument("filename")
def remove(filename: str):
    """Remove a document from the index."""
    settings = Settings()
    if not settings.openai_api_key:
        click.echo(click.style("Error: OPENAI_API_KEY is not set.", fg="red"))
        raise SystemExit(1)

    pipeline = IngestionPipeline(settings)
    stats = pipeline.remove_document(filename)
    click.echo(click.style(f"Removed {stats['removed_chunks']} chunks for '{filename}'.", fg="green"))


def main():
    cli()


if __name__ == "__main__":
    main()
