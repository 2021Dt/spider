var lF = "zxcvbnmlkjhgfdsaqwertyuiop0987654321QWERTYUIOPLKJHGFDSAZXCVBNM"
  , fne = lF + "-@#$%^&*+!";
function qu(e=[]) {
    return e.map(t => fne[t]).join("")
}
function dne(e, t) {
    switch (arguments.length) {
    case 1:
        return parseInt(Math.random() * e + 1, 10);
    case 2:
        return parseInt(Math.random() * (t - e + 1) + e, 10);
    default:
        return 0
    }
}
function hne(e) {
    return [...Array(e)].map( () => lF[dne(0, 61)]).join("")
}
function pne(e) {
    let t = "";
    return typeof e == "object" ? t = Object.keys(e).map(n => `${n}=${e[n]}`).sort().join("&") : typeof e == "string" && (t = e.split("&").sort().join("&")),
    t
}
function uK(y) {
    return finalize(y)
}
function t1(e={}) {
    const {p: t, t: n, n: u, k: o} = e
      , r = pne(t);
    return uK(u + o + decodeURIComponent(r) + n)
}

const CryptoJS = require("crypto-js");

function sha256(input) {
    // X-Dgi_Signature 的加密
    const hash = CryptoJS.SHA256(input);
    return hash.toString(CryptoJS.enc.Hex); // 返回十六进制字符串
}
console.log(sha256(input = '2NME1iwOmxJdBNMQk8tUyS$mkeyword=&openConvert=false&pageNo=30&pageSize=10&projectType=&publishEndTime=&publishStartTime=&secondType=A&siteCode=44&thirdType=[]&tradingProcess=&type=trading-type1726814600230'))
function decrypt(way,pageNo){
    //way 为请求方法 post get
    // pageNo 为请求页数

    a = Date.now();
    l = hne(16);
    c = qu([8, 28, 20, 42, 21, 53, 65, 6]);
    d = {
        [qu([56, 62, 52, 11, 23, 62, 39, 18, 16, 62, 54, 25, 25])]: qu([11, 11, 0, 21, 62, 25, 24, 19, 20, 15, 7]),
        [qu([56, 62, 52, 11, 23, 62, 39, 18, 16, 62, 60, 24, 5, 2, 18])]: l,
        [qu([56, 62, 52, 11, 23, 62, 39, 18, 16, 62, 40, 23, 6, 18, 14, 20, 15, 6, 25])]: a
    };
    console.log(d);
}
decrypt('post',30);

