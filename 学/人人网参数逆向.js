function bytesToWords(e) {
    for (var t = [], n = 0, r = 0; n < e.length; n++,
    r += 8)
        t[r >>> 5] |= e[n] << 24 - r % 32;
    return t
}
function rotl(e, t) {
    return e << t | e >>> 32 - t
}

function endian(e) {
    if (e.constructor == Number)
        return 16711935 & rotl(e, 8) | 4278255360 & rotl(e, 24);
    for (var t = 0; t < e.length; t++)
        e[t] = endian(e[t]);
    return e
}
function stringToBytes(e) {
    for (var t = [], n = 0; n < e.length; n++)
        t.push(255 & e.charCodeAt(n));
    return t
}
function stringToBytes2(e) {
    return stringToBytes(unescape(encodeURIComponent(e)))
}

function a(e,n=undefined) {
    e.constructor == String ? e = n && "binary" === n.encoding ? stringToBytes(e) : stringToBytes2(e) : i(e) ? e = Array.prototype.slice.call(e, 0) : Array.isArray(e) || e.constructor === Uint8Array || (e = e.toString());
    for (var s = bytesToWords(e), l = 8 * e.length, c = 1732584193, u = -271733879, f = -1732584194, d = 271733878, p = 0; p < s.length; p++)
        s[p] = 16711935 & (s[p] << 8 | s[p] >>> 24) | 4278255360 & (s[p] << 24 | s[p] >>> 8);
    s[l >>> 5] |= 128 << l % 32,
    s[14 + (l + 64 >>> 9 << 4)] = l;
    var h = function(e, t, n, r, i, o, a) {
        var s = e + (t & n | ~t & r) + (i >>> 0) + a;
        return (s << o | s >>> 32 - o) + t
    }
        , v = function(e, t, n, r, i, o, a) {
        var s = e + (t & r | n & ~r) + (i >>> 0) + a;
        return (s << o | s >>> 32 - o) + t
    }
        , m = function(e, t, n, r, i, o, a) {
        var s = e + (t ^ n ^ r) + (i >>> 0) + a;
        return (s << o | s >>> 32 - o) + t
    }
        , g = function(e, t, n, r, i, o, a) {
        var s = e + (n ^ (t | ~r)) + (i >>> 0) + a;
        return (s << o | s >>> 32 - o) + t
    };
    for (p = 0; p < s.length; p += 16) {
        var y = c
            , b = u
            , w = f
            , x = d;
        c = h(c, u, f, d, s[p + 0], 7, -680876936),
        d = h(d, c, u, f, s[p + 1], 12, -389564586),
        f = h(f, d, c, u, s[p + 2], 17, 606105819),
        u = h(u, f, d, c, s[p + 3], 22, -1044525330),
        c = h(c, u, f, d, s[p + 4], 7, -176418897),
        d = h(d, c, u, f, s[p + 5], 12, 1200080426),
        f = h(f, d, c, u, s[p + 6], 17, -1473231341),
        u = h(u, f, d, c, s[p + 7], 22, -45705983),
        c = h(c, u, f, d, s[p + 8], 7, 1770035416),
        d = h(d, c, u, f, s[p + 9], 12, -1958414417),
        f = h(f, d, c, u, s[p + 10], 17, -42063),
        u = h(u, f, d, c, s[p + 11], 22, -1990404162),
        c = h(c, u, f, d, s[p + 12], 7, 1804603682),
        d = h(d, c, u, f, s[p + 13], 12, -40341101),
        f = h(f, d, c, u, s[p + 14], 17, -1502002290),
        u = h(u, f, d, c, s[p + 15], 22, 1236535329),
        c = v(c, u, f, d, s[p + 1], 5, -165796510),
        d = v(d, c, u, f, s[p + 6], 9, -1069501632),
        f = v(f, d, c, u, s[p + 11], 14, 643717713),
        u = v(u, f, d, c, s[p + 0], 20, -373897302),
        c = v(c, u, f, d, s[p + 5], 5, -701558691),
        d = v(d, c, u, f, s[p + 10], 9, 38016083),
        f = v(f, d, c, u, s[p + 15], 14, -660478335),
        u = v(u, f, d, c, s[p + 4], 20, -405537848),
        c = v(c, u, f, d, s[p + 9], 5, 568446438),
        d = v(d, c, u, f, s[p + 14], 9, -1019803690),
        f = v(f, d, c, u, s[p + 3], 14, -187363961),
        u = v(u, f, d, c, s[p + 8], 20, 1163531501),
        c = v(c, u, f, d, s[p + 13], 5, -1444681467),
        d = v(d, c, u, f, s[p + 2], 9, -51403784),
        f = v(f, d, c, u, s[p + 7], 14, 1735328473),
        u = v(u, f, d, c, s[p + 12], 20, -1926607734),
        c = m(c, u, f, d, s[p + 5], 4, -378558),
        d = m(d, c, u, f, s[p + 8], 11, -2022574463),
        f = m(f, d, c, u, s[p + 11], 16, 1839030562),
        u = m(u, f, d, c, s[p + 14], 23, -35309556),
        c = m(c, u, f, d, s[p + 1], 4, -1530992060),
        d = m(d, c, u, f, s[p + 4], 11, 1272893353),
        f = m(f, d, c, u, s[p + 7], 16, -155497632),
        u = m(u, f, d, c, s[p + 10], 23, -1094730640),
        c = m(c, u, f, d, s[p + 13], 4, 681279174),
        d = m(d, c, u, f, s[p + 0], 11, -358537222),
        f = m(f, d, c, u, s[p + 3], 16, -722521979),
        u = m(u, f, d, c, s[p + 6], 23, 76029189),
        c = m(c, u, f, d, s[p + 9], 4, -640364487),
        d = m(d, c, u, f, s[p + 12], 11, -421815835),
        f = m(f, d, c, u, s[p + 15], 16, 530742520),
        u = m(u, f, d, c, s[p + 2], 23, -995338651),
        c = g(c, u, f, d, s[p + 0], 6, -198630844),
        d = g(d, c, u, f, s[p + 7], 10, 1126891415),
        f = g(f, d, c, u, s[p + 14], 15, -1416354905),
        u = g(u, f, d, c, s[p + 5], 21, -57434055),
        c = g(c, u, f, d, s[p + 12], 6, 1700485571),
        d = g(d, c, u, f, s[p + 3], 10, -1894986606),
        f = g(f, d, c, u, s[p + 10], 15, -1051523),
        u = g(u, f, d, c, s[p + 1], 21, -2054922799),
        c = g(c, u, f, d, s[p + 8], 6, 1873313359),
        d = g(d, c, u, f, s[p + 15], 10, -30611744),
        f = g(f, d, c, u, s[p + 6], 15, -1560198380),
        u = g(u, f, d, c, s[p + 13], 21, 1309151649),
        c = g(c, u, f, d, s[p + 4], 6, -145523070),
        d = g(d, c, u, f, s[p + 11], 10, -1120210379),
        f = g(f, d, c, u, s[p + 2], 15, 718787259),
        u = g(u, f, d, c, s[p + 9], 21, -343485551),
        c = c + y >>> 0,
        u = u + b >>> 0,
        f = f + w >>> 0,
        d = d + x >>> 0
    }
    return endian([c, u, f, d])      
};

function wordsToBytes(e) {
    for (var t = [], n = 0; n < 32 * e.length; n += 8)
        t.push(e[n >>> 5] >>> 24 - n % 32 & 255);
    return t
}
function bytesToHex(e) {
    for (var t = [], n = 0; n < e.length; n++)
        t.push((e[n] >>> 4).toString(16)),
        t.push((15 & e[n]).toString(16));
    return t.join("")
}
function bytesToString(e) {
    for (var t = [], n = 0; n < e.length; n++)
        t.push(String.fromCharCode(e[n]));
    return t.join("")
}

function encrypt(e){
    console.log(a(e));
    var r = wordsToBytes(a(e));
    console.log(r);
    return  bytesToHex(r) //bytesToString(r) :
}

console.log(encrypt('456456'))