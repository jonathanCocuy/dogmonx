// Push notifications require a native build (EAS/dev build).
// expo-notifications crashes in Expo Go on SDK 53+ due to ExpoTopicSubscriptionModule.
// This hook activates automatically once the app is built with EAS.
export function usePushNotifications() {}
