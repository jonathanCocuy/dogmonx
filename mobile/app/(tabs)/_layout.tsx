import { Ionicons } from '@expo/vector-icons';
import { BlurView } from 'expo-blur';
import { Tabs } from 'expo-router';
import { Platform, StyleSheet, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { colors, fonts } from '../../constants/theme';

type IoniconsName = React.ComponentProps<typeof Ionicons>['name'];

const TAB_ICONS: Record<string, { active: IoniconsName; inactive: IoniconsName }> = {
  index:   { active: 'videocam',      inactive: 'videocam-outline' },
  two:     { active: 'document-text', inactive: 'document-text-outline' },
  history: { active: 'time',          inactive: 'time-outline' },
};

function GlassPill() {
  return (
    <View style={styles.pillOuter}>
      <BlurView intensity={80} tint="dark" style={styles.blur}>
        <View style={styles.overlay} />
      </BlurView>
    </View>
  );
}

const NAV_THEME = {
  dark: true,
  colors: {
    primary: '#FFFFFF',
    background: '#2E2E2E',
    card: 'transparent',
    text: '#FFFFFF',
    border: 'transparent',
    notification: '#FF453A',
  },
};

export default function TabLayout() {
  const { bottom } = useSafeAreaInsets();

  return (
    <Tabs
      theme={NAV_THEME as any}
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarIcon: ({ focused, color }) => {
          const icons = TAB_ICONS[route.name] ?? { active: 'ellipse', inactive: 'ellipse-outline' };
          return (
            <Ionicons
              name={focused ? icons.active : icons.inactive}
              size={24}
              color={color}
            />
          );
        },
        tabBarActiveTintColor: '#FFFFFF',
        tabBarInactiveTintColor: 'rgba(255,255,255,0.38)',
        tabBarLabelStyle: {
          fontFamily: fonts.medium,
          fontSize: 11,
          letterSpacing: 0.2,
          marginTop: 2,
        },
        tabBarStyle: {
          position: 'absolute',       // flota sobre el contenido
          left: 0,
          right: 0,
          bottom: (bottom || 16) + 8,
          height: 64,
          backgroundColor: 'transparent',
          borderTopWidth: 0,
          elevation: 0,
          shadowOpacity: 0,
          paddingHorizontal: 24,
          overflow: Platform.OS === 'android' ? 'hidden' : 'visible',
        },
        tabBarBackground: () => <GlassPill />,
      })}
    >
      <Tabs.Screen name="index"   options={{ title: 'En vivo' }} />
      <Tabs.Screen name="two"     options={{ title: 'Reporte' }} />
      <Tabs.Screen name="history" options={{ title: 'Historial' }} />
    </Tabs>
  );
}

const styles = StyleSheet.create({
  pillOuter: {
    position: 'absolute',
    top: 0,
    bottom: 0,
    left: 24,
    right: 24,
    borderRadius: 26,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.4,
    shadowRadius: 20,
    elevation: Platform.OS === 'android' ? 8 : 0,
  },
  blur: {
    flex: 1,
    borderRadius: 26,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.10)',
  },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(10,10,10,0.45)',
  },
});
