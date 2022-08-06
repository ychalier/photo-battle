var current_drag;

function uploadImage() {
    console.log("Starting the image uploading procedure.");
    document.getElementById("modal-upload").classList.remove("active");
    const modal_label = document.getElementById("modal-progress-label");
    const modal_progress = document.getElementById("modal-progress-progress");
    modal_label.textContent = "Initialisation";
    modal_progress.value = 0;
    document.getElementById("modal-progress").classList.add("active");
    const input_files = document.getElementById("upload-input-image").files;
    if (FileReader && input_files && input_files.length) {
        modal_label.textContent = "Mise en ligne…";
        modal_progress.value = 1;
        const form_data_imgbb = new FormData();
        form_data_imgbb.append("key", IMGBB_APIKEY);
        form_data_imgbb.append("image", input_files[0]);
        fetch(`https://api.imgbb.com/1/upload`, {
            method: "POST",
            body: form_data_imgbb,
        }).then(res => res.json()).then(data => {
            if (data.status == 200 && data.success) {
                modal_label.textContent = "Enregistrement sur le serveur…";
                modal_progress.value = 2;
                const team_select = document.getElementById("upload-select-team");
                const form_data_server = new FormData();
                form_data_server.append("csrfmiddlewaretoken", CSRF_TOKEN);
                form_data_server.append("action", "upload_image");
                form_data_server.append("id", BATTLE_ID);
                form_data_server.append("url", data.data.image.url);
                form_data_server.append("url_thumbnail", data.data.thumb.url);
                form_data_server.append("team", team_select.options[team_select.selectedIndex].value);
                fetch(API_URL, {
                    method: "POST",
                    body: form_data_server,
                }).then(res2 => res2.json().then(data2 => {
                    if (data2.success) {
                        modal_label.textContent = "Image partagée avec succès !";
                        modal_progress.value = 3;
                        location.reload();
                    } else {
                        alert(`Impossible d'enregistrer l'image sur le serveur : ${ data2.message }`);
                    }
                }));
            } else {
                console.log(`Received an error from ImgBB (${ data.status_code } ${ data.status_txt })`);
                alert(`Impossible de mettre l'image en ligne. Réponse de l'hébergeur : "Error ${ data.error.code }, ${ data.error.message }"`);
            }
        });
    } else {
        console.log("Image not passed or FileReader not available, aborting");
        document.getElementById("modal-progress").classList.remove("active");
        alert("Impossible de charger l'image");
    }
}

function setupVote() {
    document.querySelectorAll("#modal-vote-team .modal-vote-team-button").forEach(button => {
        button.addEventListener("click", () => {
            document.querySelectorAll("#modal-vote-rank .photo-wrapper").forEach(photo_wrapper => {
                photo_wrapper.style.display = photo_wrapper.getAttribute("team") == button.getAttribute("team") ? "none" : "inline";
            });
            document.getElementById("modal-vote-rank-team").value = button.getAttribute("team");
            document.getElementById("modal-vote-team").classList.remove("active");
            document.getElementById("modal-vote-rank").classList.add("active");
        });
    });
    document.querySelectorAll("#modal-vote-rank .photo-wrapper").forEach(photo_wrapper => {
        photo_wrapper.draggable = "true";
        photo_wrapper.ondragstart = (event) => {
            console.log("Drag start", photo_wrapper);
            current_drag = photo_wrapper;
            document.querySelectorAll("#modal-vote-rank .photo-wrapper").forEach(photo_wrapper_sub => {
                if (photo_wrapper_sub != current_drag) {
                    photo_wrapper_sub.classList.add("hint");
                }
            });
        }
        photo_wrapper.ondragenter = (event) => {
            console.log("Drag enter", photo_wrapper);
            if (photo_wrapper != current_drag) {
                photo_wrapper.classList.add("active");
            }
        }
        photo_wrapper.ondragleave = (event) => {
            console.log("Drag leave", photo_wrapper);
            photo_wrapper.classList.remove("active");
        }
        photo_wrapper.ondragend = (event) => {
            console.log("Drag end", photo_wrapper);
            document.querySelectorAll("#modal-vote-rank .photo-wrapper").forEach(photo_wrapper_sub => {
                photo_wrapper_sub.classList.remove("hint");
                photo_wrapper_sub.classList.remove("active");
            });
        }
        photo_wrapper.ondragover = (event) => {
            // console.log("Drag over", photo_wrapper);
            event.preventDefault();
        }
        photo_wrapper.ondrop = (event) => {
            console.log("Drag drop", photo_wrapper, current_drag);
            event.preventDefault();
            if (photo_wrapper != current_drag) {
                let current_pos = 0;
                let dropped_pos = 0;
                document.querySelectorAll("#modal-vote-rank .photo-wrapper").forEach((photo_wrapper_sub, i) => {
                    if (current_drag == photo_wrapper_sub) {
                        current_pos = i;
                    }
                    if (photo_wrapper == photo_wrapper_sub) {
                        dropped_pos = i;
                    }
                });
                console.log(current_pos, dropped_pos);
                if (current_pos < dropped_pos) {
                    photo_wrapper.parentNode.insertBefore(current_drag, photo_wrapper.nextSibling);
                } else {
                    photo_wrapper.parentNode.insertBefore(current_drag, photo_wrapper);
                }
            }
        }
    });
    document.getElementById("modal-vote-rank-button").addEventListener("click", sendVote);
}

function sendVote() {
    document.getElementById("modal-vote-rank-button").disabled = true;
    const form_data = new FormData();
    form_data.append("csrfmiddlewaretoken", CSRF_TOKEN);
    form_data.append("id", BATTLE_ID);
    form_data.append("action", "send_vote");
    form_data.append("team", document.getElementById("modal-vote-rank-team").value);
    let rank = [];
    document.querySelectorAll("#modal-vote-rank .photo-wrapper").forEach(photo_wrapper => {
        if (photo_wrapper.getAttribute("team") != document.getElementById("modal-vote-rank-team").value) {
            rank.push(photo_wrapper.getAttribute("photo"));
        }
    });
    form_data.append("ranking", rank.join(","));
    fetch(API_URL, {
        method: "POST",
        body: form_data,
    }).then(res => res.json().then(data => {
        document.getElementById("modal-vote-rank-button").removeAttribute("disabled");
        document.getElementById("modal-vote-rank").classList.remove("active");
        if (data.success) {
            alert("Merci pour votre vote !");
            location.reload();
        } else {
            alert(`Impossible d'enregistrer le vote : ${ data.message }`);
        }
    }));
}

window.addEventListener("load", () => {
    document.getElementById("btn-upload-submit").addEventListener("click", uploadImage);
    setupVote();
});