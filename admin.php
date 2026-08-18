<?php
declare(strict_types=1);
require __DIR__ . '/bootstrap.php';
$error = '';
if (isset($_GET['logout'])) {
    unset($_SESSION['seed_admin'], $_SESSION['seed_admin_last']);
    session_regenerate_id(true);
    header('Location: index.php');
    exit;
}
if (admin_ok()) {
    header('Location: index.php');
    exit;
}
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    require_csrf();
    if (hash_equals((string)cfg('admin_key'), (string)($_POST['key'] ?? ''))) {
        session_regenerate_id(true);
        $_SESSION['seed_admin'] = true;
        $_SESSION['seed_admin_last'] = time();
        header('Location: index.php');
        exit;
    }
    $error = '管理用パスワードが違います。';
}
?><!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="assets/style.css?v=1.4.0"><title>管理者モード</title></head><body>
<header><div><small>RESEARCH PLATFORM</small><h1>管理者モードを有効にする</h1></div><nav><a href="index.php">画像解析へ戻る</a><?php if(cfg('bread_url')):?><a href="<?=h(cfg('bread_url'))?>">Bread解析</a><?php endif?></nav></header>
<main><section class="card narrow"><h2>管理用パスワード</h2><p>認証後も同じ画像解析画面を使用します。解析パラメータ・履歴・環境診断のメニューだけが追加されます。</p><p class="muted">標準では最後の操作から8時間保持されます。共有端末では利用後に「管理者モード終了」を押してください。</p><form method="post"><input type="hidden" name="csrf" value="<?=h(csrf())?>"><label>管理用パスワード<input type="password" name="key" autocomplete="current-password" required autofocus></label><button class="primary">管理者モードを有効にする</button><?php if($error):?><p class="error"><?=h($error)?></p><?php endif?></form></section></main></body></html>
