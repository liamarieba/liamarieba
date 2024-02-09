

$(".nominate-button").click(function() {
    var bookId = $(this).data("book-id");
    var title = $(this).data("title");
    var author = $(this).data("author");
    var clubId = "{{ session['club_id'] }}"; 
    
    $.ajax({
        type: "POST",
        url: "/nominate_book",
        data: JSON.stringify({ 
            book_id: bookId, 
            club_id: clubId,
            title: title,
            author: author
        }),
        contentType: "application/json;charset=UTF-8",
        success: function() {
            alert("This book has been nominated.");
        },
        error: function() {
            alert("Error nominating the book.");
        }
    });
});












