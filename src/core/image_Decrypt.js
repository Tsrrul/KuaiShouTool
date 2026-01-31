//JS解密

var CryptoJS = require('crypto-js');





function xorString(_0x4dfbeb, _0x54ec08=90) {
      _0x145f04 = {
        'DrBzg': function(_0xa214ca, _0x11d78e) {
            return _0xa214ca ^ _0x11d78e;
        }
    }
      , _0x45666a = [];
    for (let _0x4f949e = 0x0; _0x4f949e < _0x4dfbeb['length']; _0x4f949e++) {
        _0x45666a['push'](String['fromCharCode'](_0x145f04['DrBzg'](_0x4dfbeb['charCodeAt'](_0x4f949e), _0x54ec08)));
    }
    return _0x45666a["join"]('');
}


function blockReverse(_0x1553c2, _0x507b68=0x8) {
      _0x154a04 = {
        'bmidT': function(_0x3b1697, _0x56305b) {
            return _0x3b1697 + _0x56305b;
        }
    };
    let _0x549b1b = '';
    for (let _0x3b8e0a = 0x0; _0x3b8e0a < _0x1553c2["length"]; _0x3b8e0a += _0x507b68) {
        const _0x4be36c = _0x1553c2["slice"](_0x3b8e0a, _0x154a04['bmidT'](_0x3b8e0a, _0x507b68));
        _0x549b1b += _0x4be36c['split']('')['reverse']()['join']('');
    }
    return _0x549b1b;
}



function base64CustomDecode(_0x563e47) {
    let STANDARD_B64;
    STANDARD_B64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
    let CUSTOM_B64
    CUSTOM_B64 = 'ZYXABCDEFGHIJKLMNOPQRSTUVWzyxabcdefghijklmnopqrstuvw9876543210-_';
      _0xe1852b = {
        'Kmxxe': function(_0x474254, _0xbc9472) {
            return _0x474254 === _0xbc9472;
        }
    };
    return _0x563e47['split']('')['map'](_0x5eb88c => {
        _0xfb5af6 = CUSTOM_B64['indexOf'](_0x5eb88c);
        return _0xe1852b['Kmxxe'](_0xfb5af6, -0x1) ? _0x5eb88c : STANDARD_B64[_0xfb5af6];
    }
    )["join"]('');
}





function aesDecrypt(_0x18996b, _0x513e44, _0x2a8716) {
      _0x34ecac = CryptoJS['enc']['Utf8']['parse'](_0x2a8716)
      , _0x906ee1 = CryptoJS['enc']['Base64']['parse'](_0x513e44)
      , _0x3d4508 = CryptoJS['enc']['Base64']['parse'](_0x18996b)
      , _0x587f0a = CryptoJS['AES']['decrypt']({
        'ciphertext': _0x3d4508
    }, _0x34ecac, {
        'iv': _0x906ee1,
        'mode': CryptoJS['mode']['CBC'],
        'padding': CryptoJS['pad']['Pkcs7']
    })
      , _0x21229c = _0x587f0a['toString'](CryptoJS['enc']['Utf8']);
    return JSON['parse'](_0x21229c);
}







function kukudemethod(_0x2aaefb, _0x3c2a8e, _0x114653) {
      _0x3d0504 = {
        'cergr': function(_0x279301, _0x40c2ad) {
            return _0x279301(_0x40c2ad);
        },
        'HAIIV': function(_0x4ab116, _0x4a05fa, _0x5a5f0f, _0x1011ff) {
            return _0x4ab116(_0x4a05fa, _0x5a5f0f, _0x1011ff);
        }
    };
    try {
        let _0xfc8468 = _0x2aaefb
          , _0x2935dd = _0x3c2a8e;
        return _0xfc8468 = _0x3d0504['cergr'](xorString, _0xfc8468),
        _0x2935dd = xorString(_0x2935dd),
        _0xfc8468 = _0x3d0504['cergr'](blockReverse, _0xfc8468),
        _0x2935dd = _0x3d0504['cergr'](blockReverse, _0x2935dd),
        _0xfc8468 = _0x3d0504['cergr'](base64CustomDecode, _0xfc8468),
        _0x2935dd = base64CustomDecode(_0x2935dd),
        _0x3d0504['HAIIV'](aesDecrypt, _0xfc8468, _0x2935dd, _0x114653);
    } catch (_0x38b13f) {
        throw _0x38b13f;
    }
}



function akk(data) {
    let n = JSON.parse(data)
    let e = kukudemethod(n.data, n.iv, "12345678901234567890123456789013");
    return e
}


