import React from 'react';
import clsx from 'clsx';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Chatbot from '../components/Chatbot/Chatbot';
import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <h1 className="hero__title">{siteConfig.title}</h1>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            Start Reading - ⏱️
          </Link>
        </div>
      </div>
    </header>
  );
}

function HomepageCards() {
  return (
    <section className={styles.features}>
      <div className="container padding-vert--lg">
        <div className="row">
          {/* Module 1 Card */}
          <div className="col col--4 fade-in-up">
            <div className="text--center padding-horiz--md">
              <div className={styles.cardIcon} style={{fontSize: '2rem', marginBottom: '1rem'}}>🤖</div>
              <h3 className="text--center padding-horiz--md">Module 1: The Robotic Nervous System</h3>
              <p>Master ROS 2 as the communication backbone for humanoid robots</p>
              <Link className="button button--primary button--outline" to="/docs/module-1/intro">
                Explore
              </Link>
            </div>
          </div>

          {/* Module 2 Card */}
          <div className="col col--4 fade-in-up-delay-1">
            <div className="text--center padding-horiz--md">
              <div className={styles.cardIcon} style={{fontSize: '2rem', marginBottom: '1rem'}}>🌐</div>
              <h3 className="text--center padding-horiz--md">Module 2: The Digital Twin</h3>
              <p>Learn Gazebo & Unity for physics simulation and environment modeling</p>
              <Link className="button button--primary button--outline" to="/docs/module-2/intro">
                Explore
              </Link>
            </div>
          </div>

          {/* Module 3 Card */}
          <div className="col col--4 fade-in-up-delay-2">
            <div className="text--center padding-horiz--md">
              <div className={styles.cardIcon} style={{fontSize: '2rem', marginBottom: '1rem'}}>🧠</div>
              <h3 className="text--center padding-horiz--md">Module 3: The AI-Robot Brain</h3>
              <p>Implement NVIDIA Isaac technologies for perception and navigation</p>
              <Link className="button button--primary button--outline" to="/docs/module-3/intro">
                Explore
              </Link>
            </div>
          </div>
        </div>

        <div className="row padding-top--lg">
          {/* Module 4 Card */}
          <div className="col col--4 col--offset-2 fade-in-up">
            <div className="text--center padding-horiz--md">
              <div className={styles.cardIcon} style={{fontSize: '2rem', marginBottom: '1rem'}}>🗣️</div>
              <h3 className="text--center padding-horiz--md">Module 4: Vision-Language-Action</h3>
              <p>Build cognitive humanoid systems with LLMs and multimodal interfaces</p>
              <Link className="button button--primary button--outline" to="/docs/module-4/intro">
                Explore
              </Link>
            </div>
          </div>

          {/* About Book Card */}
          <div className="col col--4 fade-in-up-delay-1">
            <div className="text--center padding-horiz--md">
              <div className={styles.cardIcon} style={{fontSize: '2rem', marginBottom: '1rem'}}>📚</div>
              <h3 className="text--center padding-horiz--md">About This Book</h3>
              <p>A comprehensive guide to embodied AI systems for software developers</p>
              <Link className="button button--primary button--outline" to="/docs/intro">
                Learn More
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Welcome to ${siteConfig.title}`}
      description="A comprehensive guide to embodied AI systems, focusing on ROS 2 as the nervous system of humanoid robots">
      <HomepageHeader />
      <main>
        <HomepageCards />
        <section className="container padding-vert--lg">
          <div className="row">
            <div className="col col--12">
              <Chatbot
                title="Book Assistant"
                subtitle="Ask me anything about humanoid robotics and AI - I can answer based on the book content!"
              />
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}
