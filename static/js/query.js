function setupQueryForm() {
  const queryForm = document.getElementById("query-form");
  if (queryForm) {
    // Ensure the form exists before attaching event listener
    queryForm.addEventListener("submit", function (event) {
      event.preventDefault();
      const query = document.getElementById("query-input").value;
      executeQuery(query);
    });
  }
}

function showLoader() {
  const loader = document.getElementById("loader");
  if (loader) {
    // Check if the loader element exists
    loader.style.display = "block";
  }
}

function hideLoader() {
  const loader = document.getElementById("loader");
  if (loader) {
    // Check if the loader element exists
    loader.style.display = "none";
  }
}

function executeQuery(topic) {
  showLoader(); // Changed from showLoadingIcon() to showLoader()
  fetch("/generate-sub-topics", {
    // Changed from '/search' to match Flask route
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ topic: topic }),
  })
    .then((response) => response.json())
    .then((data) => {
      updateSubTopics(data);
      hideLoader(); // Changed from hideLoadingIcon() to hideLoader()
    })
    .catch((error) => {
      console.error("Error:", error);
      hideLoader(); // Changed from hideLoadingIcon() to hideLoader()
    });
}

function updateQueryResults(data) {
  const container = document.getElementById("query-results-container");
  if (container) {
    // Check if the container exists
    container.innerHTML = ""; // Clear previous results
    // TODO: Process and display the query results
    // This part needs to be implemented based on how you want to display the results
  }
}

function processTopic(topic) {
  fetch("/generate-sub-topics", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ topic: topic }),
  })
    .then((response) => response.json())
    .then((data) => {
      updateSubTopics(data);
      hideLoadingIcon();
    })
    .catch((error) => {
      console.error("Error:", error);
      hideLoadingIcon();
    });
}

function updateSubTopics(data) {
  const container = document.getElementById("sub-topics-container");
  container.innerHTML = "";
  if (data.subTopics) {
    const subTopics = data.subTopics
      .split("\n")
      .filter((subTopic) => subTopic.trim().length > 0);
    queryAndDisplaySubtopics(subTopics);
  } else {
    container.textContent = "No subtopics generated.";
  }
}

function queryAndDisplaySubtopics(subTopics) {
  // Map over each subTopic to perform both Pinecone and YouTube searches
  Promise.all(
    subTopics.map((subTopic) => {
      // First fetch the Pinecone results
      const pineconePromise = fetch("/query-subtopic", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ subTopic: subTopic.trim() }),
      }).then((response) => response.json());

      // Then fetch the YouTube results
      const youtubePromise = fetch("/search_youtube", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ subTopic: subTopic.trim() }),
      }).then((response) => response.json());

      // Combine the results into a single object for each subTopic
      return Promise.all([pineconePromise, youtubePromise]).then(
        ([pineconeResults, youtubeResults]) => {
          return {
            subTopic,
            pineconeResults: pineconeResults.results,
            youtubeResults: youtubeResults.videos,
          };
        },
      );
    }),
  ).then((results) => {
    // For each subTopic, display the combined results
    results.forEach(({ subTopic, pineconeResults, youtubeResults }) => {
      displaySubtopicResults(subTopic, pineconeResults, youtubeResults);
    });
  });
}

function displaySubtopicResults(subTopic, pineconeResults, youtubeResults) {
  const container = document.getElementById("sub-topics-container");
  const subTopicDiv = document.createElement("div");
  subTopicDiv.classList.add("sub-topic");

  const title = document.createElement("h2");
  title.textContent = subTopic;
  subTopicDiv.appendChild(title);

  // Display Pinecone results
  const pineconeSection = document.createElement("div");
  const pineconeTitle = document.createElement("h3");
  pineconeTitle.textContent = "From your content";
  pineconeSection.appendChild(pineconeTitle);

  const pineconeList = document.createElement("ul");
  pineconeResults.forEach((result) => {
    const listItem = document.createElement("li");
    listItem.textContent = `${
      result.title
    } (Relevance Score: ${result.score.toFixed(2)})`;
    pineconeList.appendChild(listItem);
  });
  pineconeSection.appendChild(pineconeList);
  subTopicDiv.appendChild(pineconeSection);

  // Display YouTube results
  const youtubeSection = document.createElement("div");
  const youtubeTitle = document.createElement("h3");
  youtubeTitle.textContent = "Suggested Learning";
  youtubeSection.appendChild(youtubeTitle);

  const youtubeList = document.createElement("ul");
  youtubeResults.forEach((video) => {
    const videoItem = document.createElement("li");
    const videoLink = document.createElement("a");
    videoLink.href = `https://www.youtube.com/watch?v=${video.videoId}`;
    videoLink.textContent = video.title;
    videoLink.target = "_blank";
    videoItem.appendChild(videoLink);
    youtubeList.appendChild(videoItem);
  });
  youtubeSection.appendChild(youtubeList);
  subTopicDiv.appendChild(youtubeSection);

  container.appendChild(subTopicDiv);
}
