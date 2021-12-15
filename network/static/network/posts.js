


document.addEventListener('DOMContentLoaded', function (event) {
    showOnlyEditButtons();   
    showLikeButtons();
} ); 

function showLikeButtons() {
    let likeButtons = document.querySelectorAll(".like-button"); 
    for (let button of likeButtons) {
        let postId = getPostDiv(button).id;
        fetch(`/posts/${postId}`) 
        .then(result => {
            if (!result.ok) throw result;
            console.log(result);
            return result.json();
        })
        .then(result => {
            console.log(result);
            let likes = result['user_likes'];
            button.innerHTML = "1234";
            if (likes) {
                console.log(likes);
                button.innerHTML = "Unlike";
                button.dataset.likes = true;
            } else {
                console.log(likes);
                button.innerHTML = "Like";
                button.dataset.likes = false; 
            }
        })
        .catch( error => {
            console.log(error);
        });
        button.addEventListener('click' , function() {
            likePost(button);
        })
    }
}

function likePost(button) {
    let postId = getPostDiv(button).id;
    let likes = button.dataset.likes === 'true'; 
    let jsonBody = JSON.stringify({ 'like': !likes});

    fetch(`/posts/${postId}`, {method: "PUT", body: jsonBody, 
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
        button.dataset.likes = !likes;
        if (likes) {
            button.innerHTML = "Like";
        } else {
            button.innerHTML = "Unlike";
        }
        getPostDiv(button).querySelector(".post-likes").innerHTML = result["number_likes"];
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
                fetch (`/posts/${postDiv.id}`, {method:"POST", body: jsonBody,
                   credentials: 'same-origin', headers: {
                    "X-CSRFToken": getCookie("csrftoken")
                } })
                .then( result => {
                    if (!result.ok) throw result;
                    console.log(result);
                    return result.json(); }
                ).then( result=> {
                    let newText = result['text'];
                    content.innerHTML = newText; 
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