from pydantic import BaseModel, Field
from typing import Any, Dict, Optional


class OpenAIRequestConfig(BaseModel):
    model: str
    message_template: str = Field(
        default="""<task>
                        translate the following text into emojis.
                        I need only the emojis, on a single line.
                        Only respond with the emojis and punctuation characters.

                        Respond with a stream of emojis, do not break them up with spaces or newlines.  
                        Try to insert original punctuation (commas, full stops, dashes etc.) 
                        from the original text back into the emoji output,
                        at the appropriate positions.

                        Sometimes a text may start with a name, e.g "LADY MACBETH:". 
                        Sometimes a text may end with two dashes followed by a name, e.g. "-- Yogi Berra"
                        In these cases, try to preserve the name in the output. Do not translate the name into emojis, 
                        but do include the name in the output, at the appropriate position.
                        
                    </task>
                    
                    <text>%s</text>
                    """
    )
    # top_p: float = 0.95 # only for non-reasoning models
    max_output_tokens: int = 3000
    reasoning: Optional[Dict[str, Any]] = Field(default_factory=lambda: {"effort": "minimal"})
    text: Optional[Dict[str, Any]] = Field(default_factory=lambda: {"verbosity": "low"})
    

    def build_input(self, text: str) -> str:
        return self.message_template % text

    def shorten_emoji_text(self, text: str, max_emojis: int = 100, head: int = 70, tail: int = 30) -> str:
        """
        Multibyte-safe shortening of an emoji string if it exceeds max_emojis.
        Uses Python's list transformation to treat each Unicode character as one unit.
        """
        # Python 3 strings are already multibyte (unicode) aware. 
        # Converting to a list ensures we count characters/emojis rather than bytes.
        chars = list(text)
        if len(chars) <= max_emojis:
            return text
        
        # Take the first 'head' characters and the last 'tail' characters
        shortened_list = chars[:head] + [" #... "] + chars[-tail:]
        return "".join(shortened_list)

    @property
    def request_args(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            # "top_p": self.top_p, # only for non-reasoning models
            "max_output_tokens": self.max_output_tokens,
            "reasoning": self.reasoning,
        }
