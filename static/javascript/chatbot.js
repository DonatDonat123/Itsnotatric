var me = {};
me.avatar = "./static/fotos/dd_profile.png";

var bot = {};
bot.avatar = "./static/fotos/alien.jpg";

function formatAMPM(date) {
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    minutes = minutes < 10 ? '0'+minutes : minutes;
    var strTime = hours + ':' + minutes + ' ' + ampm;
    return strTime;
}

function scrollHardToBottom (id) {
    var div = $(id)
    //div.scrollTop(div[0].scrollHeight);
    div.animate({scrollTop: div[0].scrollHeight}, 1000)
}

function insertChat(text, user){
    var date = '2017-01-01' ;
    var date = formatAMPM(new Date());
    if (user == 'user'){
        control = '<div class="row">' +
                        '<div class="col-lg-1 col-md-1 col-1"> </div>' +
                        '<div class="col-lg-1 col-md-2 col-3">' +
                            '<img class="img-fluid" src="'+ me.avatar +'" />' +
                        '</div>' +
                        '<div class="col-lg-4 col-md-5 col-6">' +
                            '<p>'+ text +'</p>' +
                            '<p><small>'+date+'</small></p>' + '<br>'+
                        '</div>' +
                    '</div>';
    }
    else{
        control = '<div class="row">' +
                '<div class="col-lg-6 col-md-4 col-2"> </div>' +
                '<div class="col-lg-3 col-md-5 col-6 text-r">' +
                    '<p>'+ text +'</p>' +
                    '<p><small>'+date+'</small></p>' + '<br>'+
                '</div>' +
                '<div class="col-lg-1 col-md-2 col-3">' +
                    '<img class="img-fluid" src="'+ bot.avatar +'" />' +
                '</div>'
                 '</div>';
    }

    $(".chatbox").append(control);
    scrollHardToBottom(".chatbox");
    //scrollSmoothToBottom('chatbox');
}

var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on( 'connect', function() {
  socket.send( 'connected')
  room = 'room0 '
 })

var btn = $('#sendbutton').on('click', function(e){
  console.log("CLOCKED")
  e.preventDefault()
  var message = $('.inputmessage').val()
  var username = 'user'
  socket.emit('myBotEvent', {
    username: username,
    message: message,
    room:room
  })
  $('.inputmessage').val('')
  console.log("username: " + username)
  console.log("message: " + message)
  console.log("room: " + room)
})

socket.on('message', function(msg){
  console.log("Message in JS Received !!!")
  if( typeof msg.username !== 'undefined' && msg.message!=='') {
    insertChat(msg.message, msg.username)
  }
  else {
  console.log("username undefined or message empty !!!")
  console.log(msg.message)
  }

})

insertChat("Hi", 'user');
insertChat("How are you ?", 'other');
insertChat("How are you ?", 'user');
insertChat("How are you ?", 'other');