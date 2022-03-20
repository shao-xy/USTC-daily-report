# 出校报备页面逻辑

2022年3月18日出校报备功能更新，当日功能反复变化。20日功能已稳定，但此页面逻辑复杂，在此处说明。

首先是我们的选择申请类型界面：

![出校类型选择](/assets/cross-campus-choices.png)

其中只有“高新园区、先研院”（现居地）、“前往先研院、高新园区”（出校原因）和“合肥其他校区”（现居地）、“跨校区上课、实验等”（出校原因）的组合是跨校区报备，其他选择组合均为“进入校申请”或“离校申请”。截取控制此功能的内联JS代码段如下：

```javascript
$(function () {

    $('#confirm-report-hook').change(function () {
        changeOption()
    })

    $('input[name="reason"]').change(function () {
        changeOption();
    })
    $('input[name="lived"]').change(function () {
        changeOption();
    })

    $('#report-submit-btn').click(function(){
        if($(this).attr('redirect') != ''){
            window.location.href = $(this).attr('redirect');
        }
    })

    function changeOption() {
        var v1 = $('input[name="lived"]:checked').val();
        var v2 = $('input[name="reason"]:checked').val();
        var islxs = $('#is_lxs').val();
        if(v1 == 4){
            $('input[name="reason"][value="5"]').attr('disabled', 'disabled');
            $('input[name="reason"][value="5"]').prop('checked', false);
        }else{
            $('input[name="reason"][value="5"]').attr('disabled', false);
        }

        if(v1 && v2){
            var url = '';
            var text = '请选择';
            if(v2 == 1){
                url = 'https://weixine.ustc.edu.cn/2020/inout_apply?t='+v1+v2
                text = '离校申请';
            }else if(v2 == 2){
                url = 'https://weixine.ustc.edu.cn/2020/stayinout_apply?t='+v1+v2
                text = '进出校申请';
            }else if(v2 == 3){
                if(v1 == 2){
                    if(islxs == 1){
                        url = 'https://weixine.ustc.edu.cn/2020/stayinout_apply?t='+v1+v2
                        text = '进出校申请';
                    }else{
                        url = 'https://weixine.ustc.edu.cn/2020/apply/daliy/i?t='+v1+v2
                        text = '跨校区报备';
                    }
                }else if(v1 == 1 || v1 == 3 || v1 == 4){
                    url = 'https://weixine.ustc.edu.cn/2020/stayinout_apply?t='+v1+v2
                    text = '进出校申请';
                }
            }else if(v2 == 4){
                if(v1 == 1){
                    if(islxs == 1){
                        url = 'https://weixine.ustc.edu.cn/2020/stayinout_apply?t='+v1+v2
                        text = '进出校申请';
                    }else{
                        url = 'https://weixine.ustc.edu.cn/2020/apply/daliy/i?t='+v1+v2
                        text = '跨校区报备';
                    }
                }else if(v1 == 2 || v1 == 3 || v1 == 4){
                    url = 'https://weixine.ustc.edu.cn/2020/stayinout_apply?t='+v1+v2
                    text = '进出校申请';
                }
            }else if(v2 == 5){
                if(v1 == 1 || v1 == 3 || v1 == 2){
                    url = 'https://weixine.ustc.edu.cn/2020/stayinout_apply?t='+v1+v2
                    text = '进出校申请';
                }
            }
            if(url && $('#confirm-report-hook').prop('checked') == true){
                $('#report-submit-btn').attr('disabled', false).attr('redirect', url).text(text);
            }else{
                $('#report-submit-btn').attr('disabled', true).attr('redirect', '').text(text);
            }

        }else{
            $('#report-submit-btn').attr('disabled', true).attr('redirect', '').text(text);
        }
    }
});
```

其中`changeOption`函数在选择选项时被调用，检查选项并控制提交按钮的功能。在这个函数里，变量`v1`和`v2`的值从选项的单选框中获得，数字和选项的对应关系在下面截取的代码中：

```html
<div class="daliy-report-form form-horizontal" style="margin-bottom: 50px;">
    <div class="form-group">
        <h5>现居地：</h5>
        <div class="checkbox clearfix">
            <label style="width: 40%;">
                <input type="radio" name="lived" value="1">
                <i></i>
                <span>高新园区、先研院</span>
            </label>
            <label style="width: 40%;">
                <input type="radio" name="lived" value="4">
                <i></i>
                <span>国金院</span>
            </label>
            <label style="width: 40%;">
                <input type="radio" name="lived" value="2">
                <i></i>
                <span>合肥其他校区</span>
            </label>
            <label style="width: 40%;">
                <input type="radio" name="lived" value="3">
                <i></i>
                <span>合肥市内校外</span>
            </label>
        </div>
    </div>
    <div class="form-group">
        <h5>出校原因：</h5>
        <div class="checkbox clearfix">
            <label style="width: 40%;">
                <input type="radio" name="reason" value="1">
                <i></i>
                <span>特殊原因前往合肥市外</span>
            </label>
            <label style="width: 40%;">
                <input type="radio" name="reason" value="2">
                <i></i>
                <span>合肥市内就医等紧急情况</span>
            </label>
            <label style="width: 40%;">
                <input type="radio" name="reason" value="3">
                <i></i>
                <span>跨校区上课、实验等</span>
            </label>
            <label style="width: 40%;">
                <input type="radio" name="reason" value="4">
                <i></i>
                <span>前往先研院、高新园区</span>
            </label>
            <label style="width: 40%;">
                <input type="radio" name="reason" value="5">
                <i></i>
                <span>前往国金院</span>
            </label>
        </div>
    </div>
</div>
```

这就是为什么带跨校区报备的脚本中，变量`CROSS_CAMPUS_TYPE`的值必须是`23`或`14`的组合的原因。
