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

function insertChat(text, user){
    var date = '2017-01-01' ;
    var date = formatAMPM(new Date());
    if (user == 'Dennis'){
        control = '<li style="width:100%">' +
                        '<div class="msj macro">' +
                            '<div class="avatar_user"><img class="img-left" style="width:100%;" src="'+ me.avatar +'" /></div>' +
                            '<div class="text text-l">' +
                                '<p>'+ text +'</p>' +
                                '<p><small>'+date+'</small></p>' + '<br>'+
                            '</div>' +
                        '</div>' +
                    '</li>';
    }
    else{
        control = '<li style="width:100%">' +
                        '<div class="msj macro">' +
                            '<div class="avatar_other"><img class="img-right" style="width:100%;" src="'+ bot.avatar +'" /></div>' +
                            '<div class="text text-r">' +
                                '<p>'+ text +'</p>' +
                                '<p><small>'+date+'</small></p>' +'<br>'+
                            '</div>' +
                        '</div>' +
                    '</li>';
    }


    $("ul.message_holder").append(control).scrollTop($("ul").prop('scrollHeight'));

}

var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on( 'connect', function() {
  socket.send( 'connected')
  room = 'room0 '
 })

var btn = $('#sendbutton').on('click', function(e){
  e.preventDefault()
  var username = $('.username').val()
  var message = $('.message').val()
  socket.emit('myBotEvent', {
    username: username,
    message: message,
    room:room
  })
  $('.message').val('')
  console.log("username: " + username)
  console.log("message: " + message)
  console.log("room: " + room)
})

var roombtn = $('#roombutton').on('click', function(e){
  e.preventDefault()
  var username = $('.username').val()
  room = e.target.value // declare globally
  socket.emit('join', {
    username: username,
    room: room
  })
  console.log("username: " + username)
  console.log("room: " + room)
})

socket.on('message', function(msg){
  console.log("Message in JS Received !!!")
  if( typeof msg.username !== 'undefined' && msg.message!=='') {
    $( 'h3' ).remove()
    //$( 'ul.message_holder' ).append( '<div><b style="color: #000">'+msg.username+'</b> '+msg.message+'</div>' )
    insertChat(msg.message, msg.username)
  }
  else {$('h3').text(msg)}
})

//insertChat("Hi", 'user')
//insertChat("How are you ?", 'other')
//insertChat("Anybody here ?", 'user')
//insertChat("I'm all alone ...", 'user')
//insertChat("Anyone... ?", 'other')