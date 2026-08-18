<?php
declare(strict_types=1);
return [
    'app_name' => 'Seed Morphology Analyzer',
    'app_version' => '2.4.0',
    'timezone' => 'Asia/Tokyo',
    'bread_url' => '../bread/',
    'db' => [
        'host' => 'localhost', 'port' => 3306,
        'name' => 'BREADで使用中のデータベース名',
        'user' => 'BREADで使用中のDBユーザー',
        'pass' => 'BREADで使用中のDBパスワード',
    ],
    'admin_key' => 'CHANGE_THIS_TO_A_LONG_RANDOM_KEY',
    'admin_session_seconds' => 8 * 60 * 60,
    'python' => [
        'binary' => '/home/a-pages/python/venv/bin/python',
        'script' => __DIR__ . '/python/seed_analyze.py',
        'timeout_seconds' => 120,
    ],
    'max_upload_bytes' => 12 * 1024 * 1024,
    'max_concurrent_analyses' => 2,
    'analysis_slot_wait_seconds' => 30,
    'job_retention_hours' => 24,
];
