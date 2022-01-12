document.addEventListener('DOMContentLoaded', function (event) {
    showOnlyEditButtons();   
    updateAllPosts();
    addLikeButtonEventListeners();
}); 

// return JsonResponse({ 'text': postObject.text, 'user_likes': likes, 
// 'number_likes': postObject.likes.count() } , status =201 )

//  return JsonResponse({"message": "Post successfully edited"}, status = 201 ) 
//PUT request with 'text' field

function updatePost(post) {
    fetch(`/posts/${post.id}`) 
    .then(result => {
        if (!result.ok) throw result;
        console.log(result);
        return result.json();
    })
    .then(result => {
        console.log(result);
        let number_likes = result['number_likes'];
        let user_likes = result['user_likes'] === true;
        let text = result['text'];

        post.querySelector('.post-likes').innerHTML = number_likes;            
        post.querySelector('.post-text').innerHTML = text ;

        let button = post.querySelector('.like-button');
        console.log('likes');
        console.log(result['user_likes'], typeof(result['user_likes']), user_likes, typeof(user_likes)  );

        if (button !== null) {
            if (user_likes) {
                button.dataset.likes = true;
                button.innerHTML = "Unlike";
            } else {
                button.dataset.likes = false;
                button.innerHTML = "Like";  
            }
        } 
    })
    .catch( error => {
        console.log(error);
    });
}

function addLikeButtonEventListeners() {
    let likeButtons = document.querySelectorAll(".like-button");
    for (let button of likeButtons) {
        if (button !== null) {
            button.addEventListener('click' , function() {
                likePost(button);
            })
        }
    }
}

function updateAllPosts() {
    let posts = document.querySelectorAll(".post");
    for (let post of posts) { 
        updatePost(post);
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function likePost(button) {
    let postId = getPostDiv(button).id;
    let user_likes = button.dataset.likes === 'true';
    let requestMethod = user_likes === true ? "DELETE" : "PUT"; 

    fetch(`/posts/${postId}/like`, {method: requestMethod, 
    credentials: 'same-origin', headers: {
        "X-CSRFToken": getCookie("csrftoken")
    }
    })
    .then(result => {
        if (!result.ok) throw result;
        console.log(result);
        return result.json();
    })
    .then( result => {
        console.log(result);
        updatePost(getPostDiv(button));
    })
    .catch( error => {
        console.log(error);
    }
    );
}

function getPostDiv (element) {
    while (element.className != 'post') {
        element = element.parentElement; 
    }
    return element; 
}

function showEditPost(button) {

    button.style.display = 'none';
    let sibling = button.parentElement.querySelector(".edit-area");
    
    let textarea = sibling.querySelector("textarea");
    textarea.style.resize = "both";

    let saveEdit = sibling.querySelector('button');

    let postDiv = getPostDiv(sibling); 
    
    let content = postDiv.querySelector(".post-text");

    fetch(`/posts/${postDiv.id}`) 
    .then(result => {
        if (!result.ok) throw result;
        console.log(result);
        return result.json();
    }).then(result => {
        console.log(result);
        textarea.value = result['text'];
        content.style.display = 'none'; 
        sibling.style.display = 'block';
        saveEdit.addEventListener('click', function (event) {
            let text  = textarea.value.trim();
            let length = text.length; 
            if (length < 1) {
                alert ("The edited text must have at least one non whitespace character");
            } else {
                let jsonBody = JSON.stringify( {'text': text });
                fetch (`/posts/${postDiv.id}`, {method:"PUT", body: jsonBody,
                   credentials: 'same-origin', headers: {
                    "X-CSRFToken": getCookie("csrftoken")
                } })
                .then( result => {
                    if (!result.ok) throw result;
                    console.log(result);
                    return result.json(); }
                ).then( result=> {
                    /*
                    let newText = result['text'];
                    content.innerHTML = newText; 
                    */
                    updatePost(getPostDiv(button));
                    sibling.style.display = 'none';
                    content.style.display = 'inline';
                    button.style.display = 'inline-block';
                }).catch( error => {
                    console.log(error);
                    alert(error);
                });
            }
        })
    }).catch( error => {
        console.log(error);
    });
}

//edit-text  >  edit-button , edit-area 
function showOnlyEditButtons() {
    let editables = document.querySelectorAll(".edit-text");

    for (let editable of editables) {
        let editArea = editable.querySelector(".edit-area");
        editArea.style.display = 'none';
        let button = editable.querySelector(".edit-button");

        button.addEventListener('click', function() {
            showEditPost(button);
        })
    }
}