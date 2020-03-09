/**
 * Created by qq272 on 2016/4/24.
 */
var express =require('express');
var mysql =require('mysql');

var connection=mysql.createConnection({
        host     : '127.0.0.1',
        user     :  'root',
        password : '',
        database : 'jd_comment',
}
);
//开始连接数据库
connection.connect(function (err) {
    if(err){
        console.log('[query] - :'+err);
    }

    console.log('[connection connect]  succeed!');
});