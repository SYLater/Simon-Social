var title = document.title;
var count = 0;
var time = new Date().getTime();
var search = document.getElementById("value_lable");
// search.remove();

 
document.querySelectorAll(".idk").forEach((b) => {
  console.log(b);
  b.onmouseleave = (e) => {
    e.target.style.background = "black";
    e.target.style.borderImage = null;
  };

  b.addEventListener("mousemove", (e) => {
    const rect = e.target.getBoundingClientRect();
    const x = e.clientX - rect.left; //x position within the element.
    const y = e.clientY - rect.top; //y position within the element.
    e.target.style.background = `radial-gradient(circle at ${x}px ${y}px , rgba(255,255,255,0.2),rgba(255,255,255,0) )`;
    e.target.style.borderImage = `radial-gradient(20% 75% at ${x}px ${y}px ,rgba(255,255,255,0.7),rgba(255,255,255,0.1) ) 1 / 1px / 0px stretch `;
  });
});

// Changes page title to notify a new message
function changeTitle() {
  count++;
  var newTitle = "(" + count + ") " + title;
  document.title = newTitle;
}

// reset page title to default
function resetTitle() {
  document.title = title;
  count = 0;
}

// update title if user is focused on another tab and a message is send
function checkTabFocused() {
  if (document.visibilityState === "visible") {
    resetTitle();
  } else {
    changeTitle();
  }
}

//when user focuses on another tab emit that the user is idle
document.addEventListener("visibilitychange", (event) => {
  console.log('eventlistener');
  if (document.visibilityState === "visible") {
    socket.emit("online", {});
  } else {
    socket.emit("idle", {});
  }
});

// when tab is closed emit that the user is offline
window.onbeforeunload = function () {
  socket.emit("offline", {});
};

function joinchat(d) {
  socket.emit("JoinGroup", { Name: d.getAttribute("value") });
  var text = d.getAttribute("value");
  var room = "chat";
  $.ajax({
    url: "/UserPresence",
    type: "get",
    data: { jsdata: text, data: room },
    success: function (response) {
      $("#Userpresence").html(response);
    },
    error: function (xhr) {
      //Do Something to handle error
    },
  });
  $.ajax({
    url: "/AllMessages",
    type: "get",
    data: { jsdata: text },
    success: function (response) {
      $("#AllMessages").html(response);
    },
    error: function (xhr) {
      //Do Something to handle error
    },
  });
  console.log('Joined chat: ' + text);
}

function PrivateMessage(d) {
  socket.emit("PrivateMessage", { Name: d.getAttribute("value") });
  var text = d.getAttribute("value");
  var room = "DM";
  $.ajax({
    url: "/UserPresence",
    type: "get",
    data: { jsdata: text, data: room },
    success: function (response) {
      $("#Userpresence").html(response);
    },
    error: function (xhr) {
      //Do Something to handle error
    },
  });
  $.ajax({
    url: "/PrivMessages",
    type: "get",
    data: { jsdata: text },
    success: function (response) {
      $("#AllMessages").html(response);
    },
    error: function (xhr) {
      //Do Something to handle error
    },
  });

  console.log('Joined chat: ' + text);
}

function createDm(d) {
  socket.emit("CreateDm", { Name: d.getAttribute("value") });
  console.log('Joined chat: ' + d.getAttribute("value"));
  location.reload();
}

function UserSearch(d) {
  var text = $(d).val();
  console.log('form');
  $.ajax({
    url: "/UserSearch",
    type: "get",
    data: { jsdata: text },
    success: function (response) {
      $("#place_for_suggestions").html(response);
    },
    error: function (xhr) {
      //Do Something to handle error
    }
  });
}

function userAddDm() {
  document.getElementById("user-add-dm").style.display = "block";
  document.getElementById("UserDMs").style.display = "none";
}

function closeForm() {
  document.getElementById("user-add-dm").style.display = "none";
}
