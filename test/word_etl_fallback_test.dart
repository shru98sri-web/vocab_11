import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:voca_11/main.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('loads bundled vocabulary when the API and cache are unavailable',
      () async {
    SharedPreferences.setMockInitialValues({});

    final result = await HttpOverrides.runZoned<Future<EtlWordsResult>>(
      () => WordEtl.run(),
      createHttpClient: (_) => throw const SocketException('offline'),
    );

    expect(result.report.source, 'bundled dataset');
    expect(result.words, isNotEmpty);
  });
}
