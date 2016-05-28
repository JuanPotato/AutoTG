var bot_api = {
    Types:   [],
    Methods: []
};

$("h4").each(function(i, e) {
    if ($(e).next().prop("tagName") == "P" &&
        $(e).next().next().prop("tagName") == "TABLE") {
        var type = true;
        var a = {};
        a.name = $(e).text();
        a.desc = $(e).next().text();
        a.fields = [];
        $(e).next().next().children().children().each(function(i) {
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
            i.desc	   = f[3];
            a.fields.push(i);
        });
        if (type)
            bot_api.Types.push(a);
        else
            bot_api.Methods.push(a);
    }
});

console.log(JSON.stringify(bot_api));
