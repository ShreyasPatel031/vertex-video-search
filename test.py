import logging
from visionai.python.gapic.visionai import visionai_v1
from visionai.python.net import channel
import streamlit as st
from datetime import timedelta

# Constants for the existing setup
PROJECT_ID = "applied-ai-practice00"
PROJECT_NUMBER = "653524927160"
REGION = "us-central1"
ENV = "PROD"

INDEX_ENDPOINT_ID = "ie-17121567812913042082"
CORPUS_ID = "9012545256067295047"
INDEX_ID = "index-7912126009553124814"

# Logging configuration
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
_logger = logging.getLogger("VisionAI")

# Helper function to query VisionAI
def fetch_search_results(query):
    try:
        warehouse_endpoint = channel.get_warehouse_service_endpoint(channel.Environment[ENV])
        warehouse_client = visionai_v1.WarehouseClient(
            client_options={"api_endpoint": warehouse_endpoint}
        )
        _logger.info("Warehouse Client initialized.")

        # Construct the index endpoint name
        index_endpoint_name = f"projects/{PROJECT_NUMBER}/locations/{REGION}/indexEndpoints/{INDEX_ENDPOINT_ID}"

        search_request = visionai_v1.SearchIndexEndpointRequest(
            index_endpoint=index_endpoint_name,
            text_query=query,
            page_size=10
        )
        return warehouse_client.search_index_endpoint(search_request).search_result_items
    except Exception as e:
        _logger.error(f"Error during search: {e}", exc_info=True)
        return []

# Generate video URLs for assets
def generate_video_urls(asset_names):
    warehouse_endpoint = channel.get_warehouse_service_endpoint(channel.Environment[ENV])
    warehouse_client = visionai_v1.WarehouseClient(
        client_options={"api_endpoint": warehouse_endpoint}
    )
    uris = []
    for asset_name in asset_names:
        try:
            retrieval_url = warehouse_client.generate_retrieval_url(
                visionai_v1.GenerateRetrievalUrlRequest(name=asset_name)
            )
            uris.append(retrieval_url.signed_uri)
        except Exception as e:
            _logger.error(f"Error generating retrieval URL for {asset_name}: {e}")
    return uris

# Function to extract seconds
def get_seconds(timestamp):
    try:
        return int(timestamp.timestamp())
    except Exception as e:
        _logger.error(f"Error extracting seconds: {e}", exc_info=True)
        return 0

# Streamlit App
def main():
    st.set_page_config(page_title="VisionAI Video Search", page_icon="🎥")

    # Add logo and title
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTEzx_ldJvB_IKoIwn1HQKxrlToO5C1cyddSA&s", use_column_width=True)  # Replace with your logo URL
    with col2:
        st.title("Simmons Video Search")

    st.markdown(
    """
    <style>
    button {
        height: auto;
        padding-top: 20px !important;
        padding-bottom: 20px !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
    
    # Input for search query with button next to it
    col1, col2 = st.columns([4, 2])
    with col1:
        query = st.text_input("Enter your search term:", value="customers")
    with col2:
        search_clicked = st.button("Search")

    if search_clicked:
        st.write("Fetching results...")
        results = fetch_search_results(query)

        if not results:
            st.write("No results found.")
        else:
            # Fetch asset names and start times
            video_data = [
                (result.asset, timedelta(seconds=get_seconds(result.segment.start_time)))
                for result in results
            ]
            st.write(f"Found {len(video_data)} results.")

            # Generate video URLs
            video_urls = generate_video_urls([data[0] for data in video_data])

            # Display videos in a grid
            cols = st.columns(2)  # Adjust number of columns as needed
            for i, (video_url, start_time, asset_name) in enumerate(zip(video_urls, [data[1] for data in video_data], [data[0] for data in video_data])):
                shortened_title = asset_name.split("/")[-1][:20] + "..." if len(asset_name) > 20 else asset_name  # Shorten asset name

                with cols[i % 2]:  # Dynamically place videos in columns
                    st.video(video_url, format="video/mp4", start_time=start_time)
                    st.markdown(f"<div style='font-size: 12px; font-weight: bold; text-align: center;'></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
