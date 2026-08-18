<?php
declare(strict_types=1);
require __DIR__.'/bootstrap.php';
$appVersion=require __DIR__.'/version.php';
$isAdmin=admin_ok();
?><!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>使い方 | <?=h(cfg('app_name'))?></title><link rel="stylesheet" href="assets/style.css?v=<?=h($appVersion)?>"></head><body>
<header><div><small>RESEARCH PLATFORM</small><h1>🌾 Seed Morphology Analyzer</h1><p>使い方ガイド <strong>Version <?=h($appVersion)?></strong></p></div><nav><a href="index.php">画像解析</a><a href="help.php">使い方</a><?php if($isAdmin):?><a href="settings.php">解析設定</a><a href="history.php">履歴</a><a href="diagnose.php">環境診断</a><a href="admin.php?logout=1">管理モード終了</a><?php else:?><a href="admin.php">管理モード</a><?php endif;?><?php if(cfg('bread_url')):?><a href="<?=h(cfg('bread_url'))?>">🍞 Bread解析</a><?php endif;?></nav></header>
<main>
<section class="card"><h2>このアプリでできること</h2><p>種子を撮影した画像から、OpenCVを使って粒数を数え、種子ごとの面積・長径・短径・長短径比・円形度・充実度・向きなどを測定します。解析結果は保存され、履歴確認、再解析、CSV出力、画像ダウンロード、手動補正ができます。</p></section>
<section class="card"><h2>基本的な使い方</h2><ol><li><b>種子を撮影します。</b> 白い無地背景に種子を並べ、できるだけ真上から撮影します。</li><li><b>「画像解析」を開きます。</b> 試料名・班名と、必要に応じてメモを入力します。</li><li><b>画像を選択します。</b> スマートフォンではカメラ、写真ライブラリ、ファイルから選べます。</li><li><b>必要なら解析範囲（ROI）を指定します。</b> 画像の一部分だけを解析したい場合に使います。</li><li><b>「形態解析して保存」を押します。</b> 粒数と個体別の形態データが表示され、結果が履歴に保存されます。</li></ol></section>
<section class="card tips"><b>撮影のコツ</b><span>白い無地背景、真上から撮影、強い影を避け、種子同士を少し離して並べると安定します。完全に重なった種子は2D画像だけでは正確に分離できません。</span></section>
<section class="card"><h2>解析結果の見方</h2><div class="grid"><div><b>粒数</b><p>検出された種子の総数です。</p></div><div><b>面積</b><p>画像上で種子が占める面積です。通常はpx²で表示されます。</p></div><div><b>長径・短径</b><p>種子の長い方向と短い方向の長さです。</p></div><div><b>長短径比</b><p>長径÷短径。値が大きいほど細長い形です。</p></div><div><b>円形度</b><p>1に近いほど円に近い形です。</p></div><div><b>充実度</b><p>輪郭の凹凸や欠けの程度を見る指標です。</p></div><div><b>向き</b><p>画像上での種子の傾きを示します。</p></div><div><b>平均・標準偏差など</b><p>解析した種子全体のばらつきを確認できます。</p></div></div></section>
<section class="card"><h2>解析範囲（ROI）</h2><p>画像全体ではなく、指定した範囲だけを解析できます。画像選択後にROI指定を開始し、画像上をドラッグして矩形を指定します。「画像全体に戻す」で解除できます。ROIは画像に対する比率で保存されるため、端末の表示サイズが変わっても同じ範囲を再現できます。</p></section>
<section class="card"><h2>管理モード</h2><p>管理モードでは、解析条件の調整、ライブプレビュー、既定値の保存、履歴の確認、再解析、環境診断を利用できます。</p><ul><li><b>Otsu自動：</b>通常の撮影条件ではまずこれを使います。</li><li><b>Adaptive：</b>照明ムラや影がある画像で試します。</li><li><b>背景・影補正：</b>大きな明るさのムラを補正します。</li><li><b>Watershed：</b>接触した種子を分離します。</li><li><b>CLAHE：</b>局所的なコントラストを補正します。</li><li><b>最小・最大面積：</b>小さなゴミや大きな塊を除外する目安です。</li></ul><p class="muted">条件を大きく変える前に、標準的な試料で結果を比較しながら調整することをおすすめします。</p></section>
<section class="card"><h2>手動カウント補正</h2><p>自動解析で見落としや誤検出があった場合、保存結果の詳細画面から手動補正できます。見落とした粒を追加したり、誤検出した粒を削除したりできます。自動解析結果自体は残り、補正前後の粒数と補正履歴が保存されます。</p></section>
<section class="card"><h2>履歴と再解析</h2><p>管理モードの「履歴」から過去の解析結果を確認できます。「再解析」を選ぶと、元画像、試料名、メモ、当時の解析条件を画像解析画面へ読み込みます。条件を変えて解析すると、元の記録を残したまま新しい履歴として保存されます。</p></section>
<section class="card"><h2>CSV・画像の保存</h2><p>保存結果から、個体別形態データや全体サマリーをCSVで出力できます。また、元画像と解析結果画像をダウンロードできます。Excelなどで追加の集計やグラフ作成を行う場合に利用できます。</p></section>
<section class="card"><h2>実寸（mm）で測定する場合</h2><p>「1 mmあたりのpx（pixels_per_mm）」を設定すると、pxだけでなくmm・mm²への換算ができます。同じ撮影面に既知サイズのスケールを置くなどして、1 mmが画像上で何pxに相当するかを求めてください。撮影距離が変わると値も変わります。</p></section>
<section class="card"><h2>対応画像と注意点</h2><ul><li>対応：JPEG、PNG、WebP</li><li>HEIC / HEIFは現在のOpenCV環境では直接扱えないため、JPEG等に変換して使用してください。</li><li>背景、照明、撮影距離、種子の色や品種によって検出結果は変わります。</li><li>研究で比較する場合は、できるだけ同じ撮影条件を使用してください。</li></ul></section>
<section class="card"><h2>うまく検出できないとき</h2><ol><li>まず撮影条件を見直します。強い影、模様のある背景、斜め撮影を避けます。</li><li>管理モードでライブプレビューを使い、Otsu／Adaptiveを切り替えます。</li><li>背景・影補正やCLAHEを試します。</li><li>小さなゴミが多い場合は最小面積を調整します。</li><li>接触粒が分離されない場合はWatershedと分離しきい値を調整します。</li><li>サーバーやPythonの状態が疑わしい場合は「環境診断」を確認します。</li></ol></section>
<section class="card"><h2>Version <?=h($appVersion)?></h2><p>Version 2.4.0では、解析パラメータの数値入力とスライダーの双方向同期、ライブプレビューの操作改善、履歴からの再解析を新規解析と同じ画面に統合する改善を行っています。</p></section>
<p><a class="button" href="index.php">画像解析へ戻る</a></p>
</main></body></html>
