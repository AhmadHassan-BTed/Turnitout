class BaseTransformer:
    """Base class/interface for all text transformers in the pipeline."""
    category = "generic"

    def transform(self, text: str, rng, line_num: int = 0, context_lines=None) -> str:
        """
        Applies a specific text transformation to the given text line.
        
        Args:
            text: The text to be transformed (potentially with placeholders).
            rng: A random.Random instance for deterministic randomness.
            line_num: The index of the line in the document.
            context_lines: Surrounding lines of prose for context.
            
        Returns:
            The transformed text string.
        """
        raise NotImplementedError
