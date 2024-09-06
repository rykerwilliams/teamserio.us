document.addEventListener("DOMContentLoaded", function() {
    const cardLinks = document.querySelectorAll('.card-link');
  
    cardLinks.forEach(link => {
      link.addEventListener('mouseenter', function() {
        const cardName = this.getAttribute('data-cardname');
        const cardImageURL = `https://api.scryfall.com/cards/named?exact=${encodeURIComponent(cardName)}`;
        
        // Fetch card details from Scryfall
        fetch(cardImageURL)
          .then(response => response.json())
          .then(data => {
            if (data.image_uris && data.image_uris.normal) {
              // Update the CSS variable with the card image URL
              this.style.setProperty('--hover-card-image', `url(${data.image_uris.normal})`);
            }
          })
          .catch(error => console.error('Error fetching card image:', error));
      });
    });
  });
  