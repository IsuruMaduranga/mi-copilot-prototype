
data = {
    "chat_history": [
        {
            "role": "user",
            "content": "Who are you"
        }
    ]
}

async function fetchAndLogJSONStream() {
    // Fetch the resource
    const response = await fetch('http://localhost:8000/generate-synapse', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
  
    let result = '';
  
    // Read the stream
    while (true) {
      const { done, value } = await reader.read();
      if (done) break; // Exit the loop when the stream is finished
      
      // Decode the stream chunk to text
      const chunk = decoder.decode(value, { stream: true });
      result += chunk;
  
      // Assuming the stream is line-delimited JSON (NDJSON)
      // Split the accumulated result into lines and parse each line as JSON
      const lines = result.split('\n');
      // Process all lines except the last, incomplete line
      for (let i = 0; i < lines.length - 1; i++) {
        try {
          const json = JSON.parse(lines[i]);
          console.log(json); // Log the parsed JSON object
        } catch (error) {
          console.error('Error parsing JSON:', error);
        }
      }
      // Keep the incomplete line for the next chunk processing
      result = lines[lines.length - 1];
    }
  
    // Handle any remaining data
    if (result) {
      try {
        const json = JSON.parse(result);
        console.log(json); // Log the last JSON object
      } catch (error) {
        console.error('Error parsing JSON:', error);
      }
    }
  }
  

fetchAndLogJSONStream();
