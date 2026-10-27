import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from 'expo-router';
import React, { useCallback, useState } from 'react';
import { ActivityIndicator, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { WebView } from 'react-native-webview';
import { ENDPOINTS } from '../../constants/api';
import { colors, fonts, radius } from '../../constants/theme';

export default function LiveScreen() {
  const { top } = useSafeAreaInsets();
  const [loading, setLoading] = useState(true);
  const [streamError, setStreamError] = useState(false);
  const [key, setKey] = useState(0);

  const reload = useCallback(() => {
    setStreamError(false);
    setLoading(true);
    setKey(k => k + 1);
  }, []);

  useFocusEffect(useCallback(() => {
    reload();
  }, []));

  const html = `<!DOCTYPE html>
<html>
<body style="margin:0;background:#2E2E2E;display:flex;align-items:center;justify-content:center;height:100vh;overflow:hidden;">
  <img src="${ENDPOINTS.videoStream}"
    style="width:100%;height:100%;object-fit:contain;"
    onerror="this.parentElement.style.display='none'" />
</body>
</html>`;

  return (
    <View style={[styles.container, { paddingTop: top + 16 }]}>
      <View style={styles.header}>
        <Text style={styles.title}>En vivo</Text>
        <View style={styles.rightRow}>
          <TouchableOpacity onPress={reload} style={styles.reloadBtn} activeOpacity={0.7}>
            <Ionicons name="refresh" size={18} color={colors.textSecondary} />
          </TouchableOpacity>
          <View style={styles.livePill}>
            <View style={[styles.liveDot, streamError && styles.liveDotOff]} />
            <Text style={styles.liveText}>{streamError ? 'OFF' : 'LIVE'}</Text>
          </View>
        </View>
      </View>

      <View style={styles.streamContainer}>
        {streamError ? (
          <View style={styles.errorBox}>
            <Text style={styles.errorIcon}>📷</Text>
            <Text style={styles.errorTitle}>Sin señal</Text>
            <Text style={styles.errorSub}>Verificá que el backend esté{'\n'}corriendo y la URL sea correcta</Text>
            <TouchableOpacity onPress={reload} style={styles.retryBtn} activeOpacity={0.7}>
              <Ionicons name="refresh" size={16} color={colors.text} />
              <Text style={styles.retryText}>Reintentar</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <>
            <WebView
              key={key}
              source={{ html }}
              style={styles.webview}
              onLoadEnd={() => setLoading(false)}
              onError={() => { setStreamError(true); setLoading(false); }}
              onHttpError={() => { setStreamError(true); setLoading(false); }}
              scrollEnabled={false}
              bounces={false}
            />
            {loading && (
              <View style={styles.overlay}>
                <ActivityIndicator size="small" color={colors.textSecondary} />
              </View>
            )}
          </>
        )}
      </View>

      <Text style={styles.url} numberOfLines={1}>{ENDPOINTS.videoStream}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bg,
    paddingBottom: 120,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingBottom: 14,
  },
  title: {
    fontFamily: fonts.jakartaBold,
    fontSize: 28,
    color: colors.text,
    letterSpacing: -0.5,
  },
  rightRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  reloadBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.surfaceHigh,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: colors.border,
  },
  livePill: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: colors.surfaceHigh,
    borderRadius: 20,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderWidth: 1,
    borderColor: colors.border,
  },
  liveDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: colors.red,
  },
  liveDotOff: {
    backgroundColor: colors.textTertiary,
  },
  liveText: {
    fontFamily: fonts.semiBold,
    fontSize: 11,
    color: colors.textSecondary,
    letterSpacing: 1,
  },
  streamContainer: {
    flex: 1,
    marginHorizontal: 16,
    borderRadius: radius.lg,
    overflow: 'hidden',
    backgroundColor: colors.surface,
  },
  webview: {
    flex: 1,
    backgroundColor: colors.bg,
  },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.bg,
  },
  errorBox: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
    paddingHorizontal: 32,
  },
  errorIcon: {
    fontSize: 48,
    marginBottom: 4,
  },
  errorTitle: {
    fontFamily: fonts.jakartaBold,
    fontSize: 22,
    color: colors.text,
    letterSpacing: -0.3,
  },
  errorSub: {
    fontFamily: fonts.regular,
    fontSize: 15,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: 22,
  },
  retryBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    backgroundColor: colors.surfaceHigh,
    borderRadius: 20,
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderWidth: 1,
    borderColor: colors.border,
    marginTop: 4,
  },
  retryText: {
    fontFamily: fonts.medium,
    fontSize: 14,
    color: colors.text,
  },
  url: {
    fontFamily: fonts.regular,
    fontSize: 11,
    color: colors.textTertiary,
    textAlign: 'center',
    paddingVertical: 10,
    paddingHorizontal: 20,
  },
});
