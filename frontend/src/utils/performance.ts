/**
 * Performance monitoring utilities
 * Tracks loading times and component render performance
 */

import React from 'react';

interface PerformanceMetric {
  name: string;
  startTime: number;
  endTime?: number;
  duration?: number;
}

class PerformanceMonitor {
  private metrics: Map<string, PerformanceMetric> = new Map();
  private isEnabled: boolean = process.env.NODE_ENV === 'development';

  /**
   * Start timing a metric
   */
  start(metricName: string) {
    if (!this.isEnabled) return;

    this.metrics.set(metricName, {
      name: metricName,
      startTime: performance.now()
    });
  }

  /**
   * End timing a metric and calculate duration
   */
  end(metricName: string) {
    if (!this.isEnabled) return;

    const metric = this.metrics.get(metricName);
    if (metric) {
      const endTime = performance.now();
      const duration = endTime - metric.startTime;
      
      metric.endTime = endTime;
      metric.duration = duration;
      
      console.log(`⚡ ${metricName}: ${duration.toFixed(2)}ms`);
      
      this.metrics.set(metricName, metric);
      return duration;
    }
  }

  /**
   * Get all recorded metrics
   */
  getMetrics() {
    return Array.from(this.metrics.values()).filter(metric => metric.duration);
  }

  /**
   * Get total page load time
   */
  getPageLoadTime() {
    const navigationTiming = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    if (navigationTiming) {
      return navigationTiming.loadEventEnd - navigationTiming.navigationStart;
    }
    return null;
  }

  /**
   * Get largest contentful paint
   */
  getLCP() {
    return new Promise<number>((resolve) => {
      new PerformanceObserver((entryList) => {
        const entries = entryList.getEntries();
        const lastEntry = entries[entries.length - 1];
        resolve(lastEntry.startTime);
      }).observe({ entryTypes: ['largest-contentful-paint'] });
    });
  }

  /**
   * Get first input delay
   */
  getFID() {
    return new Promise<number>((resolve) => {
      new PerformanceObserver((entryList) => {
        const entries = entryList.getEntries();
        const firstEntry = entries[0];
        resolve(firstEntry.processingStart - firstEntry.startTime);
      }).observe({ entryTypes: ['first-input'] });
    });
  }

  /**
   * Get cumulative layout shift
   */
  getCLS() {
    let clsValue = 0;
    new PerformanceObserver((entryList) => {
      const entries = entryList.getEntries();
      entries.forEach((entry: any) => {
        if (!entry.hadRecentInput) {
          clsValue += entry.value;
        }
      });
    }).observe({ entryTypes: ['layout-shift'] });
    
    return clsValue;
  }

  /**
   * Log comprehensive performance report
   */
  async logPerformanceReport() {
    if (!this.isEnabled) return;

    console.group('📊 Performance Report');
    
    // Page load metrics
    const pageLoadTime = this.getPageLoadTime();
    if (pageLoadTime) {
      console.log(`🚀 Page Load Time: ${pageLoadTime.toFixed(2)}ms`);
    }

    // Core Web Vitals
    try {
      const lcp = await this.getLCP();
      console.log(`🎯 Largest Contentful Paint: ${lcp.toFixed(2)}ms`);
      
      // LCP performance assessment
      if (lcp < 2500) {
        console.log('✅ LCP is GOOD (< 2.5s)');
      } else if (lcp < 4000) {
        console.log('⚠️ LCP needs improvement (2.5s - 4s)');
      } else {
        console.log('❌ LCP is POOR (> 4s)');
      }
    } catch (e) {
      console.log('❌ Could not measure LCP');
    }

    // Custom metrics
    const customMetrics = this.getMetrics();
    if (customMetrics.length > 0) {
      console.group('🔧 Custom Metrics');
      customMetrics.forEach(metric => {
        console.log(`${metric.name}: ${metric.duration?.toFixed(2)}ms`);
      });
      console.groupEnd();
    }

    console.groupEnd();
  }

  /**
   * Clear all metrics
   */
  clear() {
    this.metrics.clear();
  }
}

// Export singleton instance
export const performanceMonitor = new PerformanceMonitor();

/**
 * React hook for measuring component render time
 */
export const usePerformanceMetric = (metricName: string) => {
  const start = () => performanceMonitor.start(metricName);
  const end = () => performanceMonitor.end(metricName);
  
  return { start, end };
};

/**
 * Higher-order component for measuring component performance
 */
export function withPerformanceMetric<T extends object>(
  Component: React.ComponentType<T>,
  metricName: string
) {
  return function WrappedComponent(props: T) {
    React.useEffect(() => {
      performanceMonitor.start(`${metricName}-render`);
      return () => {
        performanceMonitor.end(`${metricName}-render`);
      };
    }, []);

    React.useEffect(() => {
      performanceMonitor.start(`${metricName}-mount`);
      return () => {
        performanceMonitor.end(`${metricName}-mount`);
      };
    }, []);

    return React.createElement(Component, props);
  };
}

/**
 * Measure API request performance
 */
export const measureApiCall = async <T>(
  name: string,
  apiCall: () => Promise<T>
): Promise<T> => {
  performanceMonitor.start(`api-${name}`);
  try {
    const result = await apiCall();
    performanceMonitor.end(`api-${name}`);
    return result;
  } catch (error) {
    performanceMonitor.end(`api-${name}`);
    throw error;
  }
};
