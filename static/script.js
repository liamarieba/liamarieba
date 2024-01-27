


function nominateForVote(button) {
    const bookId = button.getAttribute("data-book-id");

    fetch('/nominate_book', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ book_id: bookId, club_id: clubId }), 
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Book nominated successfully') {
            alert(`Book with ID ${bookId} nominated for vote!`);
        } else {
            alert('Failed to nominate the book.');
        }
    })
    .catch(error => {
        console.error('Error nominating the book:', error);
        alert('An error occurred while nominating the book.');
    });
}


















