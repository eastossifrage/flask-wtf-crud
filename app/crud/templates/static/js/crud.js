$(document).ready(function () {
    $('[data-toggle="offcanvas"]').click(function () {
        $('.row-offcanvas').toggleClass('active')
    });
    $('ul.list-group > li > a[href="' + document.location.pathname + '"]').parent().addClass('active');

    namespace='/websocket/user_refresh';
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
    console.log(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    $("#url_show").text("websocket URL: " + location.protocol + '//' + document.domain + ':' + location.port + namespace);

    socket.on('connect', function() {
        socket.emit('connect_event', {data: '我已连接上服务端！'});
    });

    socket.on('server_response', function(msg) {
        $('#log').append('<br>' + $('<div/>').text('接收 : ' + msg.data).html());
    });
    socket.on('user_response', function(msg) {
        //console.log(eval(msg.data[0]));
        //$('#users_show').append('<br>' + $('<div/>').text('接收 : ' + msg.data).html());
        var tbody = "";
        var obj = eval(msg.data[0]);
        $.each(obj, function (n, value) {
            var role = "";
            if (value.role===true){
                role = "管理员";
            }else {
                role = "一般用户";
            }
            var status = "";
            if (value.status===true){
                status = "正常";
            }else {
                status = "注销";
            }
            edit_url = "<a href=" +  location.protocol + '//' + document.domain + ':' + location.port + "/crud/websocket-edit/" + value.id + "> 修改</a>";
            delete_url = "<a href=\"javascript:delete_user_" + value.id + "()\">删除</a>";
            var trs = "";
            trs += "<tr><th>" + (n+1) + "</th><td>" + value.username + "</td><td>" + value.email + "</td><td>" + role + "</td><td>" + status + "</td><td>" + edit_url + " | " + delete_url +"</td></tr>";
            tbody += trs;
        })
        $('#users_show').empty();
        $('#users_show').append(tbody);
    });
});
