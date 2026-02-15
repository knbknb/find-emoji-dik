from pydantic import BaseModel, Field
from typing import Any, Dict, Optional


class OpenAIRequestConfig(BaseModel):
    model: str
    message_template: str = Field(
        default="""<task>
                        translate the following text into emojis.
                        I need only the emojis, on a single line.

                        Do not respond with text, except for the emojis and punctuation characters. 
                        Respond with a stream of emojis, do not break them up with spaces or newlines.  
                        Do not include any text, explanation, or commentary, just the emojis.
                        Try to insert original punctuation (commas, full stops, dashes etc.) 
                        from the original text back into the emoji output,
                        at the appropriate positions.
                        
                        If the stream of emojis is larger than 100 emojis, truncate it by taking the first 70 emojis, insert a #...',
                        then append the last 30 emojis, so that the final output is not too long 
                        but still contains the beginning and end of the emoji translation.
                    </task>
                    
                    <text>%s</text>
                    """
    )
    top_p: float = 1.0
    max_output_tokens: int = 3000
    reasoning: Optional[Dict[str, Any]] = Field(default_factory=lambda: {"effort": "minimal"})

    def build_input(self, text: str) -> str:
        return self.message_template % text

    @property
    def request_args(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "top_p": self.top_p,
            "max_output_tokens": self.max_output_tokens,
            "reasoning": self.reasoning,
        }
