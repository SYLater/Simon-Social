var socket;
$(document).ready(function () {
    socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + '/chat');

    socket.on('connect', function () {
        socket.emit('joined', {});
    });

    //joined function
    socket.on('joined', function (data) {
        console.log("joined function");
        var element = document.getElementById("user-" + data.id);
        // if (typeof (element) != 'undefined' && element != null) { }
        // else {
        //     var onlinediv = document.createElement("div");
        //     onlinediv.setAttribute("class", "online-user");
        //     onlinediv.setAttribute("id", "user-" + data.id);
        //     document.getElementById('OnlineUsers').appendChild(onlinediv);

        //     var UserImg = document.createElement("img");
        //     UserImg.setAttribute("class", "user-presence-avatar");
        //     UserImg.setAttribute("src", data.icon);
        //     UserImg.setAttribute("id", "user-presence-avatar-" + data.id);
        //     document.getElementById("user-" + data.id).appendChild(UserImg);

        //     var divheader = document.createElement('div');
        //     divheader.setAttribute("class", "headerdiv");
        //     divheader.setAttribute("id", "div-header-presence-" + data.id);
        //     document.getElementById("user-" + data.id).appendChild(divheader);

        //     var userh2 = document.createElement("h2");
        //     userh2.setAttribute("class", "name-header-presence");
        //     userh2.setAttribute("id", "name-header-presence-" + data.id);
        //     userh2.setAttribute("aria-labelledby", "username-" + data.id);
        //     document.getElementById("div-header-presence-" + data.id).appendChild(userh2);

        //     var status = document.createElement("div");
        //     status.setAttribute("class", "presence-status");
        //     status.setAttribute("id", "presence-status-" + data.id);
        //     status.innerText = data.status;
        //     document.getElementById("div-header-presence-" + data.id).appendChild(status);

        //     var username = document.createElement("span");
        //     username.setAttribute("class", "username-name-presence");
        //     username.innerText = data.username;
        //     document.getElementById("name-header-presence-" + data.id).appendChild(username);
        //     document.getElementById("user-presence-avatar-" + data.id).style.border = "2px solid green";

        //     socket.emit('online', {});
        // }
    });

    // online function
    socket.on('online', function (data) {
        console.log('online');
        document.getElementById("user-presence-avatar-" + data.id).style.border = "2px solid green";
        document.getElementById("presence-status-" + data.id).innerText = "online";
        console.log(data.username + " online function");
    });

    // offline function
    socket.on('offline', function (data) {
        console.log(data.username + " Offline function");
        var user1 = document.getElementById("user-" + data.id);
        user1.remove();
    });

    // idle function
    socket.on('idle', function (data) {
        console.log(data.username + " idle function");
        document.getElementById("user-presence-avatar-" + data.id).style.border = "2px solid orange";
        document.getElementById("presence-status-" + data.id).innerText = "idle";
    });



    socket.on('reconnect', function () {
        window.location.reload();   
        console.log("reconnect");
    });

    // Update tab when there is a message
    socket.on('message', function (data) {
        checkTabFocused();
        console.log(data.username + ' message');

    });

    $('#send').on('click', function() {
        var recipient = $('#Group').val();
        socket.emit('CreateGroup', {'Name' : recipient});
        console.log("CreateGroup");
    });

    $('#join').on('click', function() {
        var recipient = $('#Join-Group').val();
        socket.emit('JoinGroup', {'Name' : recipient});
        console.log("Join-Group");
        var element = document.getElementById("AllMessages");
        element.scrollTop = element.scrollHeight;
    });


    socket.on('JGroup',function(data){
        console.log(data.room_name);
        console.log('JGroup');
        var element = document.getElementById("AllMessages");
        element.scrollTop = element.scrollHeight;
        // var name = data.room_name;
        // var chatname = document.getElementById("current_chat_banner");
        // chatname.innerText = name;
    });

    socket.on('notification',function(data){
      console.log('notification');
      document.getElementById("user-dm-avatar-"+data.uuid).style.border = "5px solid red";
  });

    //messages
    socket.on('message', function (data) {
        // timestamp
        console.log(data.msg);
        var momentfnc = moment(data.time);
        var timesent = momentfnc.calendar();

        var messageListItem = document.createElement("li");
        messageListItem.id = "chat-messages-" + data.message_id;
        document.getElementById('AllMessagesOL').appendChild(messageListItem);

        var messagecozyMessage = document.createElement("div");
        messagecozyMessage.setAttribute("class", "messagecozyMessage");
        messagecozyMessage.setAttribute("id", "messagecozyMessage-" + data.message_id);
        messagecozyMessage.setAttribute("data-list-item-id", "chat-messages_chat-messages-" + data.message_id);
        messagecozyMessage.setAttribute("role", "article");
        messagecozyMessage.setAttribute("tabindex", "-1");
        messagecozyMessage.setAttribute("aria-setsize", "-1");
        messagecozyMessage.setAttribute("aria-roledescription", "Message");
        document.getElementById('chat-messages-' + data.message_id).appendChild(messagecozyMessage);

        var avatar = document.createElement("img");
        avatar.setAttribute("class", "user-avatar");
        avatar.setAttribute("id", "User-avatar-" + data.message_id);
        avatar.setAttribute("src", data.icon);
        avatar.setAttribute("alt", "User-" + data.user_id + "-icon");
        avatar.setAttribute("onerror", "this.src='static/images/usericons/default_icon.png'");
        document.getElementById("messagecozyMessage-" + data.message_id).appendChild(avatar);

        var contents = document.createElement("div");
        contents.setAttribute("class", "contents");
        contents.setAttribute("id", "contents-" + data.message_id);
        document.getElementById("messagecozyMessage-" + data.message_id).appendChild(contents);



        var divh2 = document.createElement('div');
        divh2.setAttribute("class", "name-time-msg");
        divh2.setAttribute("id", "name-time-div-" + data.message_id);
        document.getElementById("contents-" + data.message_id).appendChild(divh2);

        var h2 = document.createElement("span");
        h2.setAttribute("class", "name-time-header");
        h2.setAttribute("id", "name-time-header-" + data.message_id);
        h2.setAttribute("aria-labelledby", "message-username-" + data.message_id + "-message-timestamp-" + data.message_id);
        document.getElementById("name-time-div-" + data.message_id).appendChild(h2);

        var headerText = document.createElement("span");
        headerText.setAttribute('class', "headerText");
        headerText.setAttribute("id", "message-username-" + data.message_id);
        document.getElementById("name-time-header-" + data.message_id).appendChild(headerText);

        var name = document.createElement("span");
        name.setAttribute("class", "message-username-name");
        name.innerText = data.username + ' ';
        document.getElementById("name-time-header-" + data.message_id).appendChild(name);

        var timestamp = document.createElement("span");
        timestamp.setAttribute("class", "timestamp");
        timestamp.setAttribute("id", "timestamp-" + data.message_id);
        document.getElementById("name-time-header-" + data.message_id).appendChild(timestamp);

        var time = document.createElement('time');
        time.setAttribute("class", "message-timestamp");
        time.setAttribute("id", "message-timestamp-" + data.message_id);
        time.innerText = " " + " " + " " + timesent;
        document.getElementById("timestamp-" + data.message_id).appendChild(time);

        var messagecontent = document.createElement("div");
        messagecontent.setAttribute("class", "messageContent");
        messagecontent.setAttribute("id", "message-content-" + data.message_id);
        messagecontent.innerText = data.msg;
        document.getElementById("name-time-div-" + data.message_id).appendChild(messagecontent);

        console.log('message');

        var element = document.getElementById("AllMessages");
        element.scrollTop = element.scrollHeight;
    });

    socket.on('joindm', function (data) {
        var text = data.room_id;
        $.ajax({
          url: "/UserPresence",
          type: "get",
          data: { jsdata: text },
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
      })
});
