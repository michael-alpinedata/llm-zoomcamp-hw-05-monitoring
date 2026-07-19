from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("llm-zoomcamp")

from rag_helper import RAGBase

# We ues the prices from OpenAI to get a similar answer (not the google gemini's one)
INPUT_PRICE_PER_MILLION = 0.75
OUTPUT_PRICE_PER_MILLION = 4.50


class RAGTraced(RAGBase):

    def search(self, query, num_results=5):
        with tracer.start_as_current_span("search") as span:
            return super().search(query, num_results=num_results)

    def llm(self, prompt):
        with tracer.start_as_current_span("llm") as span:
            response = super().llm(prompt)

            # Q2: token usage and cost per span 
            # (cost not needed for homework but interesting anyway)
            usage = response.usage_metadata
            span.set_attribute("input_tokens", usage.prompt_token_count)
            span.set_attribute("output_tokens", usage.candidates_token_count)
    
            cost = (usage.prompt_token_count / 1_000_000) * INPUT_PRICE_PER_MILLION \
                + (usage.candidates_token_count / 1_000_000) * OUTPUT_PRICE_PER_MILLION
            span.set_attribute("cost", cost)

            return response

    def rag(self, query):
        with tracer.start_as_current_span("rag") as span:
            return super().rag(query)


if __name__ == "__main__":
    from starter import index, client
    rag = RAGTraced(index=index, llm_client=client)

    query = "How does the agentic loop keep calling the model until it stops?"
    answer = rag.rag(query)
    print(answer)