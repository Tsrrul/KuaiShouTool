//POST请求


function MD5(input) {
    // 常量定义（根据RFC 1321）
    const S = [
        7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
        5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
        4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
        6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21
    ];

    const K = [
        0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee,
        0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
        0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be,
        0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
        0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa,
        0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
        0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed,
        0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
        0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c,
        0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
        0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05,
        0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
        0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039,
        0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
        0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1,
        0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391
    ];

    // 步骤1：将输入转换为字节数组
    let bytes = [];
    if (typeof input === 'string') {
        // 使用TextEncoder处理UTF-8（现代浏览器/Node.js）
        if (typeof TextEncoder !== 'undefined') {
            const encoder = new TextEncoder();
            bytes = Array.from(encoder.encode(input));
        } else {
            // 兼容性方案（仅支持ASCII和基本BMP字符）
            for (let i = 0; i < input.length; i++) {
                const code = input.charCodeAt(i);
                if (code < 0x80) {
                    bytes.push(code);
                } else if (code < 0x800) {
                    bytes.push(0xc0 | (code >> 6));
                    bytes.push(0x80 | (code & 0x3f));
                } else if (code < 0xd800 || code >= 0xe000) {
                    bytes.push(0xe0 | (code >> 12));
                    bytes.push(0x80 | ((code >> 6) & 0x3f));
                    bytes.push(0x80 | (code & 0x3f));
                } else {
                    // 处理代理对（Surrogate Pair）
                    i++;
                    const code2 = input.charCodeAt(i);
                    const u = ((code & 0x3ff) << 10) | (code2 & 0x3ff);
                    bytes.push(0xf0 | (u >> 18));
                    bytes.push(0x80 | ((u >> 12) & 0x3f));
                    bytes.push(0x80 | ((u >> 6) & 0x3f));
                    bytes.push(0x80 | (u & 0x3f));
                }
            }
        }
    } else if (input instanceof Uint8Array) {
        bytes = Array.from(input);
    } else if (Array.isArray(input)) {
        bytes = input.slice();
    } else {
        throw new Error('输入必须是字符串、Uint8Array或字节数组');
    }

    // 步骤2：数据填充
    const originalBitLength = bytes.length * 8;

    // 追加一个1位（0x80），然后追加0位直到长度模512等于448
    bytes.push(0x80);

    // 填充0直到长度满足条件
    while ((bytes.length * 8) % 512 !== 448) {
        bytes.push(0x00);
    }

    // 步骤3：追加原始消息长度的64位表示（小端序）
    // 注意：长度是原始消息的位长度，不是填充后的长度
    const lengthBytes = new Array(8);
    let len = originalBitLength;

    // 将64位长度拆分为8个字节（小端序）
    for (let i = 0; i < 8; i++) {
        lengthBytes[i] = len & 0xff;
        len = Math.floor(len / 256); // 或者使用无符号右移：len >>> 8
    }

    // 将长度字节追加到消息中
    bytes.push(...lengthBytes);

    // 步骤4：初始化MD缓冲区（A, B, C, D）
    let A = 0x67452301;
    let B = 0xefcdab89;
    let C = 0x98badcfe;
    let D = 0x10325476;

    // 辅助函数：32位循环左移
    function rotateLeft(x, n) {
        return (x << n) | (x >>> (32 - n));
    }

    // 步骤5：处理每个512位（64字节）的消息块
    for (let blockStart = 0; blockStart < bytes.length; blockStart += 64) {
        // 将当前块划分为16个32位字（小端序）
        const M = new Array(16);

        for (let i = 0; i < 16; i++) {
            const byteIndex = blockStart + i * 4;
            M[i] = (
                bytes[byteIndex] |
                (bytes[byteIndex + 1] << 8) |
                (bytes[byteIndex + 2] << 16) |
                (bytes[byteIndex + 3] << 24)
            );
        }

        // 保存当前块的寄存器值
        let AA = A;
        let BB = B;
        let CC = C;
        let DD = D;

        // 第1轮：16次操作
        for (let i = 0; i < 16; i++) {
            let F = (BB & CC) | ((~BB) & DD);
            let g = i;
            let temp = DD;
            DD = CC;
            CC = BB;
            BB = BB + rotateLeft((AA + F + K[i] + M[g]) >>> 0, S[i]);
            AA = temp;
        }

        // 第2轮：16次操作
        for (let i = 16; i < 32; i++) {
            let F = (DD & BB) | ((~DD) & CC);
            let g = (5 * i + 1) % 16;
            let temp = DD;
            DD = CC;
            CC = BB;
            BB = BB + rotateLeft((AA + F + K[i] + M[g]) >>> 0, S[i]);
            AA = temp;
        }

        // 第3轮：16次操作
        for (let i = 32; i < 48; i++) {
            let F = BB ^ CC ^ DD;
            let g = (3 * i + 5) % 16;
            let temp = DD;
            DD = CC;
            CC = BB;
            BB = BB + rotateLeft((AA + F + K[i] + M[g]) >>> 0, S[i]);
            AA = temp;
        }

        // 第4轮：16次操作
        for (let i = 48; i < 64; i++) {
            let F = CC ^ (BB | (~DD));
            let g = (7 * i) % 16;
            let temp = DD;
            DD = CC;
            CC = BB;
            BB = BB + rotateLeft((AA + F + K[i] + M[g]) >>> 0, S[i]);
            AA = temp;
        }

        // 更新寄存器值
        A = (A + AA) >>> 0;
        B = (B + BB) >>> 0;
        C = (C + CC) >>> 0;
        D = (D + DD) >>> 0;
    }

    // 步骤6：输出最终的128位摘要（小端序转换为十六进制字符串）
    function toHex(value) {
        // 将32位整数转换为8位十六进制字符串
        let hex = value.toString(16).padStart(8, '0');
        // 小端序：反转字节顺序
        return hex.match(/.{2}/g).reverse().join('');
    }

    return toHex(A) + toHex(B) + toHex(C) + toHex(D);
}

// 测试函数
function testMD5() {
    console.log('MD5测试结果:');

    const testCases = [
        {input: '', expected: 'd41d8cd98f00b204e9800998ecf8427e'},
        {input: 'hello', expected: '5d41402abc4b2a76b9719d911017c592'},
        {input: 'Hello World', expected: 'b10a8db164e0754105b7a99be72e3fe5'},
        {input: 'The quick brown fox jumps over the lazy dog', expected: '9e107d9d372bb6826bd81d3542a419d6'},
        {input: 'The quick brown fox jumps over the lazy dog.', expected: 'e4d909c290d0fb1ca068ffaddf22cbd0'},
        {
            input: '12345678901234567890123456789012345678901234567890123456789012345678901234567890',
            expected: '57edf4a22be3c955ac49da2e2107b67a'
        }
    ];

    let allPassed = true;

    for (const testCase of testCases) {
        const result = MD5(testCase.input);
        const passed = result === testCase.expected;
        allPassed = allPassed && passed;

        console.log(`输入: "${testCase.input.length > 20 ? testCase.input.substring(0, 20) + '...' : testCase.input}"`);
        console.log(`结果: ${result}`);
        console.log(`预期: ${testCase.expected}`);
        console.log(`状态: ${passed ? '✓ 通过' : '✗ 失败'}`);
        console.log('---');
    }

    if (allPassed) {
        console.log('✅ 所有测试用例通过！');
    } else {
        console.log('❌ 部分测试用例失败！');
    }

    return allPassed;
}


function replaceBD(_0x5908aa) {
    return _0x5908aa['replace'](/b/g, '#')['replace'](/d/g, 'b')['replace'](/#/g, 'd');
}

function generateSignatureWithMD5(_0x34feba, _0x1624be, _0x32634c, _0x1a872c) {
    _0x320466 = {
        'jvsVW': function (_0x2def63, _0x4bda82) {
            return _0x2def63(_0x4bda82);
        }
    }
        , _0x3358d9 = Object['keys'](_0x34feba)['sort']()
        , _0x198683 = _0x3358d9['map'](_0x276648 => _0x276648 + '=' + _0x34feba[_0x276648])['join']('&')
        , _0x1dcc50 = _0x198683 + '&salt=' + _0x1624be + '&ts=' + _0x32634c + '&secret=' + _0x1a872c
        , _0x5365f1 = _0x320466['jvsVW'](MD5, _0x1dcc50);
    return _0x320466['jvsVW'](replaceBD, _0x5365f1);
}


function createSignedParamsMD5(_0x27773c, _0x4cf14c = '5Q0NvQxD0zdQ5RLQy5xs') {
    _0x2248af = {
        'yEaLM': function (_0x1d07a3, _0x38cf14) {
            return _0x1d07a3 / _0x38cf14;
        },
        'VWDXl': function (_0x3e32bf, _0x43aa4e, _0x1fb10e, _0x51729f, _0x34b90c) {
            return _0x3e32bf(_0x43aa4e, _0x1fb10e, _0x51729f, _0x34b90c);
        }
    }
        , _0x4f72c7 = Math['floor'](_0x2248af['yEaLM'](Date['now'](), 1000))
        , _0x1301ad = Math['random']()['toString'](36)['substring'](2, 10)
        , _0x3f543d = _0x2248af['VWDXl'](generateSignatureWithMD5, _0x27773c, _0x1301ad, _0x4f72c7, _0x4cf14c);
    return {
        ..._0x27773c,
        'ts': _0x4f72c7,
        'salt': _0x1301ad,
        'sign': _0x3f543d
    };
}

function json_data(url) {
    r = {requestURL: url, captchaKey: '', captchaInput: ''}
    let s = createSignedParamsMD5(r, "5Q0NvQxD0zdQ5RLQy5xs")
    return s
}

