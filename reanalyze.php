<?php
declare(strict_types=1);require __DIR__.'/bootstrap.php';require_admin();$id=(int)($_GET['id']??0);header('Location: index.php?reanalyze='.$id);exit;
