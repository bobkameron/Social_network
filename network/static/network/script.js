
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

    let follows = button.dataset.follows === 'true';
    let requestMethod = follows ? "DELETE" : "PUT";     
    let profileId = getProfileId();

    console.log( 'clickfollows ', 'follows:', follows, 'requestmethod:', requestMethod);    

    fetch(`/users/${profileId}/follow`, {method: requestMethod,
    credentials: 'same-origin', headers: {
        "X-CSRFToken": getCookie("csrftoken")
    }
    })
    .then(result => {
        if (!result.ok) throw result;
        console.log(result);
        setFollowButtonAndFollowers(); 
        return result.json();
    }).then(result => {
        console.log(result);  
    }).catch( error => {
        console.log(error);
    });
}

/*
JsonResponse({'user_follows':response, 'number_followers': followers, 
        'number_following':following}, status = 200)
*/

function setFollowButtonAndFollowers () {
    let followButton = getFollowButton();
    let profileId = getProfileId();
    let numberFollowers = document.querySelector("#number-followers");
    let numberFollowing = document.querySelector("#number-following");
    fetch(`/users/${profileId}/info`, {method: "GET" })
    .then(result => {
        if (!result.ok) throw result;
        console.log(result);
        return result.json();
    }).then(result => {

        userFollows = result['user_follows'];
        console.log(userFollows, typeof(userFollows), 'follows');

        if (userFollows === true) {
            followButton.innerHTML = "Unfollow";
            followButton.dataset.follows = true; 
        } else {
            followButton.innerHTML = "Follow";
            followButton.dataset.follows = false;
        }
        numberFollowers.innerHTML = result['number_followers'];
        numberFollowing.innerHTML = result['number_following'];
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
    followButton = getFollowButton();
    followButton.style.display = 'block';
    setFollowButtonAndFollowers ();
    followButton.addEventListener( 'click', function (event) {
        clickFollows();
    })
    /*
    let followCount = document.querySelector('#follow-count');

    let followButton = document.createElement('button');
    followButton.style.marginLeft = "45%";
    followButton.id = "follow-button";
    insertAfter(followButton, followCount);
    setFollowButtonAndFollowers();
    
    });
    */

}
