# js逆向hook的详细写法总结

## js逆向hook的详细写法总结
通过hook可以快速定位我们想要分析的代码。在js逆向之中一般使用`Object.defineProperty()`来进行`hook`

```Object.defineProperty(obj, prop, descriptor)```
> 其中`obj`是目标对象，`prop`是属性名，`descriptor`是描述符

描述符有一下几个属性和含义：
1. `value`：属性值
2. `writable`：数据描述符，目标属性的值是否可以被重写
3. `enumerable`：是否可枚举
4. `configurable`：目标属性是否可以被删除或是否可以再次修改特性
5. `get`：存取描述符，目标属性获取值的方法
6. `set`：存取描述符，目标属性设置值的方法

`Function.prototype` 是 `JavaScript` 中所有函数的原型对象，所有函数都可以访问它定义的方法和属性


### 如何编写 JavaScript Hook：详细步骤和示例
1. 确定你希望拦截哪个对象的哪些方法或属性。例如，我们想监控 `document.cookie` 的设置和获取。
2. 通过 `Object.defineProperty()` 来设置 `get` 和 `set` 方法，拦截对对象属性的访问和修改。
3. 在 `Hook` 的 `set` 和 `get` 中添加调试逻辑，以便观察变量的状态和行为。
4. 在使用 `Hook` 时，确保你处理原始逻辑。如果 `Hook` 了方法，***需要调用原始方法以保持功能***。
 

## 常见的hook方法

### Cookie Hook

> 里面有很多东西都是差不多的，可以根据具体的需求去改写对应的代码。

```js
(function() { 
    // 自执行函数，确保局部作用域
    'use strict'; // 开启严格模式，帮助捕获错误

    // 临时存储 cookie 的变量
    var cookieTemp = ""; 

    // 使用 Object.defineProperty Hook document.cookie 属性
    Object.defineProperty(document, 'cookie', {
        // 设置方法，拦截对 cookie 的赋值
        set: function(val) { 
            // 打印捕获到的 cookie 设置
            console.log('Hook 捕获到 cookie 设置 ->', val);
            debugger; // 在这里设置断点，方便调试和检查
            // 将赋值存入临时变量
            cookieTemp = val;
            // 返回赋值
            return val;
        },
        // 获取方法，拦截对 cookie 的读取
        get: function() {
            // 返回临时存储的 cookie
            return cookieTemp;
        }
    });
})();

```
还可以这样写
```js
// 临时存储 cookie 的变量
var tmpCookie = "";

// 使用 Object.defineProperty Hook document.cookie 属性
Object.defineProperty(document, "cookie", {
  // 设置方法
  set: function (value) {
    // 检查 value 是否为字符串且包含 "a1"
    if (typeof value === "string" && value.includes("a1")) {
      // 打印捕获到的 cookie 设置
      console.log("Hook 捕获到 cookie 设置 ->", value);
      // 触发调试器，方便检查
      debugger;
    }
    // 更新临时 cookie 变量
    tmpCookie = value;
    // 返回设置的值
    return value;
  },
  // 获取方法
  get: function () {
    // 返回临时 cookie 变量
    return tmpCookie;
  },
});
```

### Header Hook

```js
// 保存原始的 setRequestHeader 方法
var originalSetRequestHeader = window.XMLHttpRequest.prototype.setRequestHeader;

// 重写 XMLHttpRequest 的 setRequestHeader 方法
window.XMLHttpRequest.prototype.setRequestHeader = function (header, value) {
  // 检查请求头是否为 "Authorization"
  if (header === "Authorization") {
    // 触发调试器，方便检查
    debugger;
  }
  // 调用原始的 setRequestHeader 方法，保持功能
  return originalSetRequestHeader.apply(this, arguments);
};

```

### Hook 过 debugger

#### constructor 构造函数中的 debugger
```js
// 保存原始的 constructor
var _constructor = constructor;

// 重写 Function.prototype.constructor
Function.prototype.constructor = function (string) {
  // 检查传入的字符串是否为 "debugger"
  if (string == "debugger") {
    // 如果是，则返回 null，避免执行 debugger
    return null;
  }
  // 调用原始 constructor，保持功能
  return _constructor(string);
};

```
#### eval 构造函数中的 debugger
```js
// 自执行函数，开启严格模式
(function () {
  "use strict";
  // 保存原始的 eval 方法
  var eval_ = window.eval;

  // 重写 window.eval 方法
  window.eval = function (x) {
    // 替换 eval 中的 debugger; 为空字符串
    eval_(x.replace("debugger;", "  ; "));
  };
  // 确保重写后的 eval 方法保持原有的 toString 方法
  window.eval.toString = eval_.toString;
})();

```

### URL Hook

```js
// 保存原始的 open 方法
var originalOpen = window.XMLHttpRequest.prototype.open;

// 重写 XMLHttpRequest 的 open 方法
window.XMLHttpRequest.prototype.open = function (method, url) {
  // 检查 URL 是否为字符串且包含 "comment"
  if (typeof url === "string" && url.includes("comment")) {
    // 触发调试器，方便检查
    debugger;
  }
  // 调用原始的 open 方法，保持功能
  return originalOpen.apply(this, arguments);
};

```

### JSON.stringify Hook

```js
// 保存原始的 JSON.stringify 方法
JSON.stringify_ = JSON.stringify;

// 重写 JSON.stringify 方法
JSON.stringify = function () {
  // 检查第一个参数是否存在且包含 "time"
  if (arguments[0] && arguments[0]["time"]) {
    // 触发调试器，方便检查
    debugger;
  }
  // 调用原始的 JSON.stringify 方法并返回结果
  let result = JSON.stringify_.apply(this, arguments);
  return result; // 返回处理后的结果
};

```

### JSON.parse Hook

```js
// 保存原始的 JSON.parse 方法
JSON.parse_ = JSON.parse;

// 重写 JSON.parse 方法
JSON.parse = function () {
  // 检查第一个参数是否为字符串且包含 "ab"
  if (typeof arguments[0] === "string" && arguments[0].includes("ab")) {
    // 触发调试器，方便检查
    debugger;
  }
  // 调用原始的 JSON.parse 方法并返回结果
  return JSON.parse_.apply(this, arguments);
};

```


