class BaseTransformer:
    """Base class/interface for all text transformers in the pipeline."""
    def transform(self, text: str, context, line_num: int = 0, context_lines=None) -> str:
        """
        Applies a specific text transformation to the given text line.
        
        Args:
            text: The text to be transformed (potentially with placeholders).
            context: The TextModifier instance managing state/config/RNG.
            line_num: The index of the line in the document.
            context_lines: Surrounding lines of prose for context.
            
        Returns:
            The transformed text string.
        """
        raise NotImplementedError
