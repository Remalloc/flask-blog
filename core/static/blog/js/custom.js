var API_URL = "http://127.0.0.1:8001";
var ARTICLE_URL = API_URL + "/article";
var ADD_COMMENT_URL = API_URL + "/add";
var DEL_COMMENT_URL = ARTICLE_URL + "/del";

var ADMIN_URL = API_URL + "/admin";
var ADMIN_ARTICLE_URL = ADMIN_URL + "/article";
var ADMIN_ADD_ARTICLE_URL = ADMIN_ARTICLE_URL + "/add";
var ADMIN_DEL_ARTICLE_URL = ADMIN_ARTICLE_URL + "/del";
var ADMIN_DEL_USER_URL = ADMIN_URL + "/users/del";

var PAGE = $(".pagination").data("page");


// 解析markdown
$(document).ready(function () {
  var article = $("#markdown");
  var converter = new showdown.Converter();
  var text = article.text();
  var html = converter.makeHtml(text);
  article.html(html);
});

// 回复评论
$('#replyModal').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget); // Button that triggered the modal
  var recipient = button.data('username'); // Extract info from data-* attributes
  var floor = button.data('floor');
  var cid = button.data('cid');
  var modal = $(this);
  modal.find('.modal-title').text('回复评论');
  modal.find('.modal-body #reply-name').val(recipient + "(#" + floor + ")");
  modal.find('#reply').val(cid);
});

// 发送评论
$('#send').click(function () {
  var modal = $('#replyModal');
  var reply_name = modal.find('.modal-body #reply-name');
  var reply_content = modal.find('.modal-body #reply-content');
  reply_content.val(reply_name.val() + ": " + reply_content.val());
  $('#reply-form').submit();
});

// 删除评论
$('.del-modal').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget);
  var modal = $(this);
  var aid = button.data('aid');
  var cid = button.data('cid');
  console.log(aid);

  $('#determine_del').click(function () {
    $.get(
      DEL_COMMENT_URL,
      {
        cid: cid,
        aid: aid,
        page: PAGE
      },
      function () {
        window.location.reload();
      })
  });
});

// "个人设置"表单验证
$('.setting-form :submit').click(function () {
  var origin_password = $(".setting-form [name='origin_password']");
  var new_password = $(".setting-form [name='new_password']");
  var repeat_password = $(".setting-form [name='repeat_password']");
  var email = $(".setting-form [name='email']");
  var alert_modal = $(".alert-modal");

  if (!origin_password.val()) {
    alert_modal.find(".modal-title").text("密码输入错误");
    alert_modal.find(".modal-body").text("必须输入原密码才能修改信息");
    alert_modal.modal('show');
    return false;
  }
  else if (origin_password.val().length < 6 || origin_password.val().length > 20) {
    alert_modal.find(".modal-title").text("密码格式错误");
    alert_modal.find(".modal-body").text("原密码长度在6~20位之间");
    alert_modal.modal('show');
    return false;
  }

  if (new_password.val()) {
    if (new_password.val().length < 6 || new_password.val().length > 20) {
      alert_modal.find(".modal-title").text("密码格式错误");
      alert_modal.find(".modal-body").text("新密码长度必须在6~20位之间");
      alert_modal.modal('show');
      return false;
    }
    if (new_password.val() !== repeat_password.val()) {
      alert_modal.find(".modal-title").text("密码输入错误");
      alert_modal.find(".modal-body").text("重复密码与原密码不同");
      alert_modal.modal('show');
      return false;
    }
  }

  $(".setting-form form").submit();
  return true;
});

// 去掉时间毫秒显示
$(document).ready(function () {
  var pub_time = $(".pub-date");
  pub_time.text(pub_time.text().split('.')[0]);
});

// 管理员
function set_modal_button(modal, style) {
  if (style === "browse") {
    // 隐藏提交和取消按钮并显示修改和删除按钮
    modal.find("#send-article").css("display", "none");
    modal.find("#cancel-article").css("display", "none");
    modal.find("#modify-article").css("display", "inline");
    modal.find("#delete-article").css("display", "inline");
  }
  else if (style === "edit") {
    // 隐藏修改和删除按钮并显示提交和取消按钮
    modal.find("#modify-article").css("display", "none");
    modal.find("#delete-article").css("display", "none");
    modal.find("#send-article").css("display", "inline");
    modal.find("#cancel-article").css("display", "inline");
  }
}

$("#article-modal").on("show.bs.modal", function (event) {
  var button = $(event.relatedTarget);
  var aid = button.data("aid");
  if (aid === undefined) return;
  var modal = $(this);
  modal.attr("data-aid", aid);

  $.get(
    ADMIN_ARTICLE_URL,
    {aid: aid, page: PAGE},
    function (response) {
      modal.find('.modal-title').text(response.title);
      // 解析markdown
      var converter = new showdown.Converter();
      var html = converter.makeHtml(response.content);
      modal.find('.modal-body').html(html);
    },
    'json'
  );
  // 隐藏提交和取消按钮并显示修改和删除按钮
  set_modal_button(modal, "browse");

});


$("#modify-article").click(function () {
  var modal = $("#article-modal");
  var aid = modal.data("aid");

  $.get(
    ADMIN_ARTICLE_URL,
    {aid: aid, page: PAGE},
    function (response) {
      // 修改界面变为可编辑
      modal.find('.modal-title').html(
        "<input type='text' class='form-control' name='title' value='" + response.title + "'>"
      );
      modal.find('.modal-body').html(
        "<textarea class='form-control' name='content' rows='15'>" + response.content + "</textarea>"
      );
    },
    "json"
  );
  // 设置表单提交地址
  modal.find("form").attr("action", ADMIN_ARTICLE_URL + "?aid=" + aid);
  // 隐藏修改和删除按钮并显示提交和取消按钮
  set_modal_button(modal, "edit");
});

$("#delete-article").click(function () {
  var modal = $("#article-modal");
  var aid = modal.data("aid");
  var result = confirm("是否删除文章");
  if (result) {
    $.get(
      ADMIN_DEL_ARTICLE_URL,
      {aid: aid},
      function () {
        window.location.reload();
      });
  }
});

$("#add-article").click(function () {
  var modal = $("#article-modal");
  // 修改前必须激活模态框
  modal.modal();
  // 修改界面变为可编辑
  modal.find('.modal-title').html(
    "<input type='text' class='form-control' name='title'>"
  );
  modal.find('.modal-body').html(
    "<textarea class='form-control' name='content' rows='15'></textarea>"
  );
  // 设置表单提交地址
  modal.find("form").attr("action", ADMIN_ADD_ARTICLE_URL);
  // 隐藏修改和删除按钮并显示提交和取消按钮
  set_modal_button(modal, "edit");
});

$(".delete-user").click(function () {
  var uid = $(this).data("uid");
  var result = confirm("是否删除用户");
  if (result) {
    $.get(
      ADMIN_DEL_USER_URL,
      {uid: uid},
      function () {
        window.location.reload();
      });
  }
});

