document.addEventListener("DOMContentLoaded", function() {
    const cardLinks = document.querySelectorAll('.card-link');
  
    cardLinks.forEach(link => {
      
      link.addEventListener('mouseenter', function() {
        const cardName = this.getAttribute('data-cardname');
        


        // const cardImageURL = `https://api.scryfall.com/cards/named?exact=${encodeURIComponent(cardName)}`;
        
        //const cardImageURL = `https://api.scryfall.com/cards/named?exact=${cardName}`;
        const cardImageURL = `https://api.scryfall.com/cards/search?q=!"${cardName}"+not%3Areprint`;

        // Fetch card details from Scryfall
        fetch(cardImageURL)
          .then(response => response.json())
          .then(data => {
            if (data.data[0].image_uris && data.data[0].image_uris.normal) {
            // if (data.image_uris && data.image_uris.normal) {
              
              // get the div to display the card preview
              cardpreview = this.parentElement.parentElement.parentElement.querySelector('.card-preview')
      
              // cardpreview.style.setProperty('background-image', `url(${data.image_uris.normal})`)
              cardpreview.style.setProperty('background-image', `url(${data.data[0].image_uris.normal})`)

              // Update the CSS variable with the card image URL
              // this.style.setProperty('--hover-card-image', `url(${data.image_uris.normal})`);
            }
          })
          .catch(error => console.error('Error fetching card image:', error));
      });
    });
    
  });
  


  

  function copyDecklist(button) {
    // Find the sibling div with class 'copyable-decklist'
    const copyableDecklist = button.parentElement.querySelector('.copyable-decklist').innerText;

    // Create a temporary textarea to hold the text
    const tempTextArea = document.createElement("textarea");
    tempTextArea.value = copyableDecklist;

    // Append the textarea to the document body
    document.body.appendChild(tempTextArea);

    // Select the text and copy it to the clipboard
    tempTextArea.select();
    document.execCommand("copy");

    // Remove the temporary textarea from the document
    document.body.removeChild(tempTextArea);

    // Optional: Provide feedback to the user
    alert("Decklist copied to clipboard!");
  }