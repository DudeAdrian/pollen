"""
Anti-Addiction Hooks - Mindful Engagement Patterns

These hooks prevent addictive patterns like infinite scroll, notification spam,
and attention extraction. They promote intentional, healthy app usage.
"""

from typing import Dict, Any


class useMindfulScroll:
    """
    Hook that prevents doom-scrolling with intentional breaks.
    
    Wellness Impact:
    - Prevents loss of time awareness
    - Encourages regular breaks
    - Reduces dopamine loop formation
    - Increases user agency
    
    Anti-Pattern Replaced: Infinite scroll
    Cognitive Load: Reduced through intentional pacing
    """
    
    TYPESCRIPT_TEMPLATE = '''
import { useState, useCallback, useRef, useEffect } from 'react';

interface MindfulScrollOptions {
  itemCount: number;           // Total items available
  itemsPerBatch?: number;      // Items to show per batch (default: 10)
  enableBreathPrompts?: boolean;
  breathPromptInterval?: number; // Items between prompts (default: 10)
}

interface MindfulScrollState {
  visibleItems: number;
  showBreathPrompt: boolean;
  itemsViewed: number;
  canLoadMore: boolean;
}

/**
 * useMindfulScroll - Prevents Doom-Scrolling
 * 
 * Replaces: Infinite scroll
 * Wellness Benefits:
 * - Prevents time loss
 * - Encourages breaks
 * - Increases intentionality
 * 
 * Usage:
 * const { scrollProps, state, loadMore, dismissPrompt } = useMindfulScroll({
 *   itemCount: 100,
 *   itemsPerBatch: 10,
 *   enableBreathPrompts: true,
 * });
 * 
 * <ScrollView {...scrollProps}>
 *   {items.slice(0, state.visibleItems).map(...)}
 * </ScrollView>
 */
export function useMindfulScroll(options: MindfulScrollOptions) {
  const {
    itemCount,
    itemsPerBatch = 10,
    enableBreathPrompts = true,
    breathPromptInterval = 10,
  } = options;

  const [state, setState] = useState<MindfulScrollState>({
    visibleItems: itemsPerBatch,
    showBreathPrompt: false,
    itemsViewed: 0,
    canLoadMore: itemCount > itemsPerBatch,
  });

  const scrollStartTime = useRef<number>(Date.now());
  const lastPromptTime = useRef<number>(Date.now());

  // Track session time
  useEffect(() => {
    const interval = setInterval(() => {
      const sessionDuration = Date.now() - scrollStartTime.current;
      
      // Suggest break after 5 minutes of continuous scrolling
      if (sessionDuration > 5 * 60 * 1000 && enableBreathPrompts) {
        setState(prev => ({ ...prev, showBreathPrompt: true }));
        scrollStartTime.current = Date.now(); // Reset
      }
    }, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, [enableBreathPrompts]);

  const loadMore = useCallback(() => {
    setState(prev => {
      const newVisible = Math.min(prev.visibleItems + itemsPerBatch, itemCount);
      const shouldShowPrompt = 
        enableBreathPrompts && 
        Math.floor(newVisible / breathPromptInterval) > Math.floor(prev.visibleItems / breathPromptInterval);

      return {
        visibleItems: newVisible,
        showBreathPrompt: shouldShowPrompt,
        itemsViewed: newVisible,
        canLoadMore: newVisible < itemCount,
      };
    });
  }, [itemCount, itemsPerBatch, enableBreathPrompts, breathPromptInterval]);

  const dismissPrompt = useCallback(() => {
    setState(prev => ({ ...prev, showBreathPrompt: false }));
    lastPromptTime.current = Date.now();
  }, []);

  const onScroll = useCallback((event: any) => {
    const { contentOffset, contentSize, layoutMeasurement } = event.nativeEvent;
    const isNearBottom = 
      contentOffset.y + layoutMeasurement.height >= contentSize.height - 100;

    if (isNearBottom && state.canLoadMore && !state.showBreathPrompt) {
      loadMore();
    }
  }, [state.canLoadMore, state.showBreathPrompt, loadMore]);

  return {
    scrollProps: {
      onScroll,
      scrollEventThrottle: 16,
    },
    state,
    loadMore,
    dismissPrompt,
  };
}
'''

    WELLNESS_METADATA = {
        'anti_pattern_replaced': 'infinite_scroll',
        'wellness_benefits': [
            'prevents_time_loss',
            'encourages_breaks',
            'increases_intentionality',
            'reduces_dopamine_loops'
        ],
        'cognitive_load_impact': 'reduced',
        'hrv_impact': 'positive',
        'recommended_for': ['social_feeds', 'news_apps', 'shopping_apps']
    }


class useBreathPause:
    """
    Hook that encourages mindful breathing during app usage.
    
    Wellness Impact:
    - Reduces physiological stress
    - Increases present-moment awareness
    - Prevents compulsive usage
    - Improves HRV over time
    
    Anti-Pattern Replaced: Continuous engagement
    """
    
    TYPESCRIPT_TEMPLATE = '''
import { useState, useEffect, useCallback, useRef } from 'react';

interface BreathPauseOptions {
  intervalMinutes?: number;      // Minutes between prompts (default: 10)
  breathDuration?: number;       // Seconds for breath exercise (default: 60)
  pattern?: '4-7-8' | 'box' | 'coherent'; // Breathing pattern
  enableSounds?: boolean;
}

interface BreathPauseState {
  showPrompt: boolean;
  isBreathing: boolean;
  breathPhase: 'inhale' | 'hold' | 'exhale' | 'rest';
  sessionDuration: number; // seconds
  promptsShown: number;
  promptsCompleted: number;
}

/**
 * useBreathPause - Encourages Mindful Breathing
 * 
 * Replaces: Continuous engagement
 * Wellness Benefits:
 * - Reduces stress
 * - Increases awareness
 * - Prevents compulsive use
 * - Improves HRV
 * 
 * Usage:
 * const { state, takeBreath, dismiss, startBreathing } = useBreathPause({
 *   intervalMinutes: 10,
 *   breathDuration: 60,
 *   pattern: '4-7-8',
 * });
 * 
 * {state.showPrompt && <BreathPrompt onBreath={takeBreath} onDismiss={dismiss} />}
 */
export function useBreathPause(options: BreathPauseOptions = {}) {
  const {
    intervalMinutes = 10,
    breathDuration = 60,
    pattern = '4-7-8',
    enableSounds = false,
  } = options;

  const [state, setState] = useState<BreathPauseState>({
    showPrompt: false,
    isBreathing: false,
    breathPhase: 'rest',
    sessionDuration: 0,
    promptsShown: 0,
    promptsCompleted: 0,
  });

  const sessionStart = useRef<number>(Date.now());
  const breathInterval = useRef<NodeJS.Timeout | null>(null);

  // Check for breath prompts
  useEffect(() => {
    const checkInterval = setInterval(() => {
      const now = Date.now();
      const elapsed = now - sessionStart.current;
      
      // Show prompt every interval
      if (elapsed > intervalMinutes * 60 * 1000 && !state.showPrompt && !state.isBreathing) {
        setState(prev => ({
          ...prev,
          showPrompt: true,
          sessionDuration: Math.floor(elapsed / 1000),
        }));
      }
    }, 60000); // Check every minute

    return () => clearInterval(checkInterval);
  }, [intervalMinutes, state.showPrompt, state.isBreathing]);

  const startBreathing = useCallback(() => {
    setState(prev => ({
      ...prev,
      isBreathing: true,
      showPrompt: false,
      breathPhase: 'inhale',
    }));

    // Guide breathing pattern
    let phaseIndex = 0;
    const phases = pattern === '4-7-8' 
      ? ['inhale', 'hold', 'exhale'] 
      : ['inhale', 'hold', 'exhale', 'hold'];

    breathInterval.current = setInterval(() => {
      phaseIndex = (phaseIndex + 1) % phases.length;
      setState(prev => ({ ...prev, breathPhase: phases[phaseIndex] as any }));
    }, getPhaseDuration(pattern));

    // End breathing after duration
    setTimeout(() => {
      if (breathInterval.current) {
        clearInterval(breathInterval.current);
      }
      setState(prev => ({
        ...prev,
        isBreathing: false,
        breathPhase: 'rest',
        promptsCompleted: prev.promptsCompleted + 1,
      }));
      sessionStart.current = Date.now(); // Reset session timer
    }, breathDuration * 1000);
  }, [pattern, breathDuration]);

  const takeBreath = useCallback(() => {
    startBreathing();
    return {
      duration: breathDuration,
      pattern,
      phases: pattern === '4-7-8' ? [4, 7, 8] : [4, 4, 4, 4],
    };
  }, [startBreathing, breathDuration, pattern]);

  const dismiss = useCallback(() => {
    setState(prev => ({
      ...prev,
      showPrompt: false,
      promptsShown: prev.promptsShown + 1,
    }));
    sessionStart.current = Date.now(); // Reset timer
  }, []);

  // Cleanup
  useEffect(() => {
    return () => {
      if (breathInterval.current) {
        clearInterval(breathInterval.current);
      }
    };
  }, []);

  return {
    state,
    takeBreath,
    dismiss,
    startBreathing,
  };
}

function getPhaseDuration(pattern: string): number {
  switch (pattern) {
    case '4-7-8':
      return 4000; // Base unit
    case 'box':
      return 4000;
    case 'coherent':
      return 5500; // 5.5 second cycles
    default:
      return 4000;
  }
}
'''

    WELLNESS_METADATA = {
        'anti_pattern_replaced': 'continuous_engagement',
        'wellness_benefits': [
            'reduces_stress',
            'increases_awareness',
            'prevents_compulsive_use',
            'improves_hrv'
        ],
        'cognitive_load_impact': 'reduced',
        'hrv_impact': 'positive',
        'recommended_for': ['all_apps', 'high_stress_contexts', 'productivity_apps']
    }


class useIntentionalNotification:
    """
    Hook that batches notifications at mindful moments.
    
    Wellness Impact:
    - Reduces notification anxiety
    - Respects attention
    - Prevents interruption of flow states
    - Increases notification relevance
    
    Anti-Pattern Replaced: Notification spam
    """
    
    TYPESCRIPT_TEMPLATE = '''
import { useState, useCallback, useRef } from 'react';

interface Notification {
  id: string;
  title: string;
  body: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  scheduledAt: number;
  data?: any;
}

interface IntentionalNotificationOptions {
  deliveryMode?: 'immediate' | 'batched' | 'mindful_moments';
  batchInterval?: number; // Minutes between batch deliveries
  maxBatchSize?: number;
  respectQuietHours?: boolean;
  quietHoursStart?: number; // 24h format
  quietHoursEnd?: number;
}

interface NotificationState {
  pending: Notification[];
  delivered: Notification[];
  showBatchPrompt: boolean;
  unreadCount: number;
}

/**
 * useIntentionalNotification - Mindful Notification Batching
 * 
 * Replaces: Notification spam
 * Wellness Benefits:
 * - Reduces anxiety
 * - Respects attention
 * - Preserves flow states
 * - Increases relevance
 * 
 * Usage:
 * const { 
 *   state, 
 *   schedule, 
 *   deliverPending, 
 *   dismissBatch,
 *   setDeliveryMode 
 * } = useIntentionalNotification({
 *   deliveryMode: 'mindful_moments',
 *   batchInterval: 30,
 *   respectQuietHours: true,
 *   quietHoursStart: 22,
 *   quietHoursEnd: 8,
 * });
 * 
 * schedule({
 *   title: 'New Message',
 *   body: 'You have a new message',
 *   priority: 'medium',
 * });
 */
export function useIntentionalNotification(options: IntentionalNotificationOptions = {}) {
  const {
    deliveryMode = 'mindful_moments',
    batchInterval = 30,
    maxBatchSize = 10,
    respectQuietHours = true,
    quietHoursStart = 22,
    quietHoursEnd = 8,
  } = options;

  const [state, setState] = useState<NotificationState>({
    pending: [],
    delivered: [],
    showBatchPrompt: false,
    unreadCount: 0,
  });

  const [mode, setMode] = useState(deliveryMode);
  const batchTimer = useRef<NodeJS.Timeout | null>(null);

  const isQuietHours = useCallback(() => {
    if (!respectQuietHours) return false;
    const hour = new Date().getHours();
    if (quietHoursStart > quietHoursEnd) {
      // Overnight (e.g., 22-8)
      return hour >= quietHoursStart || hour < quietHoursEnd;
    }
    return hour >= quietHoursStart && hour < quietHoursEnd;
  }, [respectQuietHours, quietHoursStart, quietHoursEnd]);

  const schedule = useCallback((notification: Omit<Notification, 'id' | 'scheduledAt'>) => {
    const newNotification: Notification = {
      ...notification,
      id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      scheduledAt: Date.now(),
    };

    // Urgent notifications bypass batching (but respect quiet hours)
    if (notification.priority === 'urgent' && !isQuietHours()) {
      deliverImmediately(newNotification);
      return { queued: false, delivered: true };
    }

    // Immediate mode
    if (mode === 'immediate' && !isQuietHours()) {
      deliverImmediately(newNotification);
      return { queued: false, delivered: true };
    }

    // Queue for batch/mindful delivery
    setState(prev => {
      const newPending = [...prev.pending, newNotification];
      
      // Show batch prompt if we've reached threshold
      const shouldShowPrompt = newPending.length >= maxBatchSize;
      
      return {
        ...prev,
        pending: newPending,
        showBatchPrompt: shouldShowPrompt || prev.showBatchPrompt,
        unreadCount: newPending.length,
      };
    });

    // Set up batch timer if not already set
    if (!batchTimer.current && mode === 'batched') {
      batchTimer.current = setTimeout(() => {
        deliverPending();
      }, batchInterval * 60000);
    }

    return { queued: true, delivered: false };
  }, [mode, isQuietHours, maxBatchSize, batchInterval]);

  const deliverImmediately = (notification: Notification) => {
    // Platform-specific notification
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(notification.title, {
        body: notification.body,
        data: notification.data,
      });
    }

    setState(prev => ({
      ...prev,
      delivered: [...prev.delivered, notification],
    }));
  };

  const deliverPending = useCallback(() => {
    const toDeliver = [...state.pending];
    
    if (toDeliver.length === 0) return { delivered: 0 };

    // Batch notification
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(`${toDeliver.length} mindful notifications`, {
        body: `Including: ${toDeliver[0].title}${toDeliver.length > 1 ? ` and ${toDeliver.length - 1} more` : ''}`,
        data: { notifications: toDeliver },
      });
    }

    setState(prev => ({
      ...prev,
      pending: [],
      delivered: [...prev.delivered, ...toDeliver],
      showBatchPrompt: false,
      unreadCount: 0,
    }));

    // Clear batch timer
    if (batchTimer.current) {
      clearTimeout(batchTimer.current);
      batchTimer.current = null;
    }

    return { delivered: toDeliver.length };
  }, [state.pending]);

  const dismissBatch = useCallback(() => {
    setState(prev => ({ ...prev, showBatchPrompt: false }));
  }, []);

  const setDeliveryMode = useCallback((newMode: IntentionalNotificationOptions['deliveryMode']) => {
    setMode(newMode || 'mindful_moments');
  }, []);

  const clearPending = useCallback(() => {
    setState(prev => ({
      ...prev,
      pending: [],
      unreadCount: 0,
    }));
  }, []);

  return {
    state,
    schedule,
    deliverPending,
    dismissBatch,
    setDeliveryMode,
    clearPending,
    deliveryMode: mode,
  };
}
'''

    WELLNESS_METADATA = {
        'anti_pattern_replaced': 'notification_spam',
        'wellness_benefits': [
            'reduces_anxiety',
            'respects_attention',
            'preserves_flow_states',
            'increases_relevance'
        ],
        'cognitive_load_impact': 'reduced',
        'hrv_impact': 'positive',
        'recommended_for': ['all_apps', 'social_apps', 'messaging_apps']
    }


# Export all hooks
HOOK_REGISTRY = {
    'useMindfulScroll': useMindfulScroll,
    'useBreathPause': useBreathPause,
    'useIntentionalNotification': useIntentionalNotification,
}


def get_hook_metadata(hook_name: str) -> Dict[str, Any]:
    """Get wellness metadata for a hook"""
    hook = HOOK_REGISTRY.get(hook_name)
    if hook:
        return {
            'name': hook_name,
            'template': hook.TYPESCRIPT_TEMPLATE,
            **hook.WELLNESS_METADATA
        }
    return {}
