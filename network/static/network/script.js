
function getProfileId () {
    let header = document.querySelector('#profile');
    let profileId = header.dataset.profile_id;
    return profileId; 
}

document.addEventListener('DOMContentLoaded', function (event) {
    addFollowsButton();    
} ); 

function insertAfter(newNode, referenceNode) {
    referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
}

function getCSRF () {
    return getCookie('csrftoken');
    // document.querySelector('#profile').dataset.csrf;
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

function getFollowButton() {
    return document.querySelector("#follow-button");
}

function clickFollows() {
    let button = getFollowButton();
    let follows = ! (button.dataset.follows === 'true');
    let jsonBody = JSON.stringify( {'follow': follows } );
    console.log(jsonBody);
    let profileId = getProfileId();
    let csrf = getCSRF();
    fetch(`/users/${profileId}/follow`, {method: "PUT", body: jsonBody, 
    credentials: 'same-origin', headers: {
        "X-CSRFToken": getCookie("csrftoken")
    }
    })
    .then(result => {
        if (!result.ok) throw result;
        console.log(result);
        return result.json();
    }).then(result => {
        let followers = result['followers'];
        let following = result['following'];
        document.querySelector("#number-followers").innerHTML = followers;
        document.querySelector("#number-following").innerHTML = following; 
        setFollowButton();
        console.log(result);  
    }).catch( error => {
        console.log(error);
    });
}


function setFollowButton () {
    let followButton = getFollowButton();
    let profileId = getProfileId();
    fetch(`/users/${profileId}/follow`, {method: "GET" })
    .then(result => {
        if (!result.ok) throw result;
        console.log(result);
        return result.json();
    }).then(result => {
        if (result['follows']) {
            followButton.innerHTML = "Unfollow";
            followButton.dataset.follows = true; 
        } else {
            followButton.innerHTML = "Follow";
            followButton.dataset.follows = false;
        }
        console.log(result);  
    }).catch( error => {
        console.log(error);
    });
}

function addFollowsButton() {
    let hidden = document.querySelector('#logged-in');
    if (hidden === null ) return; 

    let header = document.querySelector('#profile');
    let profileId = header.dataset.profile_id;
    let userId = header.dataset.user_id; 
    
    if (profileId === userId) return; 
    
    let followCount = document.querySelector('#follow-count');

    let followButton = document.createElement('button');
    followButton.style.marginLeft = "45%";
    followButton.id = "follow-button";
    insertAfter(followButton, followCount);
    setFollowButton();
    document.querySelector("#follow-button").addEventListener( 'click', function (event) {
        clickFollows();
    }); 
}
