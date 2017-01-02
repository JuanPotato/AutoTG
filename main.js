var bot_api = {
    Types:   [],
    Methods: []
};

function next(e, n) {
    var new_e = e;
    for (i = 0; i < Math.abs(n); i++) {
        new_e = new_e.next()
    }
    return new_e
}

function nextag(e, n) {
    return next(e, n).prop('tagName')
}

$("h4").each(function(i, ee) { var e = $(ee)
    if (nextag(e, 1) == 'P' &&
          (nextag(e, 2) == 'TABLE' ||
            (nextag(e, 2) == 'BLOCKQUOTE' && nextag(e, 3) == 'TABLE') ||
            (nextag(e, 2) == 'P' && nextag(e, 3) == 'TABLE')
          )
        ) {
        var type = true;
        var a = {};
        a.name = e.text();
        a.desc = e.next().text();
        a.fields = [];
        var t = e.next().next()
        if (t.prop('tagName') != 'TABLE') t = t.next()
        t.children().children().each(function(i) {
            var f = [];
            $(this).children().each(function() {
                f.push($(this).text());
            });
            if (i === 0) {
                type = f[0] == "Field";
                return;
            }
            i = {};
            i.field = f[0];
            i.type  = f[1];
            if (type) {
                var m = f[2].match(/^Optional. (.*)$/)
                if (m != null) {
                    f[3] = m[1]
                } else {
                    f[3] = f[2]
                    f[2] = "Yes"
                }
            }
            i.required = f[2] == "Yes";
            i.desc     = f[3];
            a.fields.push(i);
        });
        if (type)
            bot_api.Types.push(a);
        else
            bot_api.Methods.push(a);
    }
});

console.log(JSON.stringify(bot_api));
