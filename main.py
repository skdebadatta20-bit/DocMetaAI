"""DocMetaAI application entrypoint."""

from ui import DocMetaAIApp


def main() -> None:
    """Initialize and run the DocMetaAI desktop application."""
    app = DocMetaAIApp()
    app.run()


if __name__ == "__main__":
    main()
