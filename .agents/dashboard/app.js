// AAC V2 Dashboard Client Logic

// Global function to switch tabs
window.switchTab = function(btn, tabId) {
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

  btn.classList.add('active');
  const targetTab = document.getElementById(tabId + '-tab');
  if (targetTab) {
    targetTab.classList.add('active');
  }
};

// Global function to toggle subtask status
window.toggleTask = async function(taskIndex, completed) {
  try {
    const res = await fetch('/api/task/toggle', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        taskIndex: taskIndex,
        completed: completed
      })
    });
    if (res.ok) {
      // Reload dashboard data instantly
      window.loadData(false);
    } else {
      console.error('Failed to toggle task status.');
    }
  } catch (err) {
    console.error('Error toggling task:', err);
  }
};

// Global function to load dashboard data
window.loadData = async function(force = false) {
  const refreshBtns = document.querySelectorAll('.btn-action');
  if (force) {
    refreshBtns.forEach(btn => {
      btn.disabled = true;
      btn.textContent = 'Auditing...';
    });
  }

  try {
    const url = force ? '/api/status?force=true' : '/api/status';
    const res = await fetch(url);
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    const data = await res.json();
    
    // Manage button states based on server auditing flag
    if (data.auditing) {
      refreshBtns.forEach(btn => {
        btn.disabled = true;
        btn.textContent = 'Auditing...';
      });
      if (currentPollSpeed !== 500) {
        window.startPolling(500); // Poll fast while auditing
      }
    } else {
      refreshBtns.forEach(btn => {
        btn.disabled = false;
        btn.textContent = 'Refresh Audit';
      });
      if (currentPollSpeed !== 5000) {
        window.startPolling(5000); // Restore slow polling
      }
    }
    
    // 1. Version Info
    const versionBadge = document.getElementById('version-badge');
    if (versionBadge) {
      versionBadge.textContent = 'v' + (data.version || '2.109.0');
    }

    // 2. Compliance Audits
    const complianceList = document.getElementById('compliance-list');
    if (complianceList) {
      complianceList.innerHTML = '';
      if (data.compliance) {
        for (const [name, passed] of Object.entries(data.compliance)) {
          const item = document.createElement('div');
          item.className = 'compliance-item';
          item.innerHTML = `
            <span class="name">${name}</span>
            <span class="status-badge ${passed ? 'pass' : 'fail'}">${passed ? 'PASS' : 'FAIL'}</span>
          `;
          complianceList.appendChild(item);
        }
      }
    }
    
    const timestamp = document.getElementById('compliance-timestamp');
    if (timestamp) {
      timestamp.textContent = 'Updated: ' + (data.timestamp || 'Just now');
    }

    // 3. Active Issue Details
    const issue = data.active_issue || { id: "None", title: "No Active Issue Checked Out", status: "closed", tasks: [], branch: "unknown" };
    const issueTitleEl = document.getElementById('active-issue-title');
    if (issueTitleEl) {
      issueTitleEl.textContent = issue.id !== 'None' ? `${issue.id}: ${issue.title}` : issue.title;
    }
    const issueBranchEl = document.getElementById('active-issue-branch');
    if (issueBranchEl) {
      issueBranchEl.textContent = issue.branch || 'unknown';
    }

    // 4. Interactive Tasks
    const activeTasksList = document.getElementById('active-tasks-list');
    if (activeTasksList) {
      activeTasksList.innerHTML = '';
      if (issue.tasks && issue.tasks.length > 0) {
        issue.tasks.forEach((task, idx) => {
          const checked = task.toLowerCase().includes('[x]');
          const cleanLabel = task.replace(/^-\s+\[\s*[xX\s]\s*\]\s*/, '');
          const item = document.createElement('div');
          item.className = 'task-item' + (checked ? ' done' : '');
          item.innerHTML = `
            <div class="task-checkbox"></div>
            <span class="task-label">${cleanLabel}</span>
          `;
          item.addEventListener('click', () => {
            window.toggleTask(idx, !checked);
          });
          activeTasksList.appendChild(item);
        });
      } else {
        activeTasksList.innerHTML = '<p class="text-muted" style="font-size: 0.85rem;">No tasks defined in the active issue file.</p>';
      }
    }

    // 5. Git Status
    const gitStatusList = document.getElementById('git-status-list');
    if (gitStatusList) {
      gitStatusList.innerHTML = '';
      if (data.git_status && data.git_status.length > 0) {
        data.git_status.forEach(file => {
          const isStaged = file.startsWith('M') || file.startsWith('A') || file.startsWith('D') || file.startsWith('R');
          const item = document.createElement('div');
          item.className = 'git-file' + (isStaged ? ' staged' : '');
          item.style.fontFamily = "'Fira Code', monospace";
          item.style.fontSize = "0.8rem";
          item.style.padding = "0.3rem 0.5rem";
          item.style.marginBottom = "0.3rem";
          item.style.borderRadius = "6px";
          item.style.background = "rgba(255, 255, 255, 0.02)";
          item.style.borderLeft = `3px solid ${isStaged ? 'var(--accent-success)' : 'var(--accent-warning)'}`;
          item.textContent = file;
          gitStatusList.appendChild(item);
        });
      } else {
        gitStatusList.innerHTML = '<p class="text-muted" style="font-size: 0.85rem;">Workspace is clean. No uncommitted modifications.</p>';
      }
    }

    // 6. Collaborative Module Locks
    const locksList = document.getElementById('locks-list');
    if (locksList) {
      locksList.innerHTML = '';
      if (data.locks && data.locks.length > 0) {
        data.locks.forEach(lock => {
          const item = document.createElement('div');
          item.className = 'lock-card-row';
          item.innerHTML = `
            <div class="lock-info-box">
              <span class="module-name">${lock.module}</span>
              <span class="holder-branch">Branch: <code>${lock.branch}</code> • ${lock.timestamp}</span>
            </div>
            <button class="btn-secondary" onclick="window.handleReleaseLock('${lock.module}')">Release</button>
          `;
          locksList.appendChild(item);
        });
      } else {
        locksList.innerHTML = '<p class="text-muted" style="font-size: 0.85rem;">No active module locks found.</p>';
      }
    }

    // 7. Lessons Learned
    const lessonsList = document.getElementById('lessons-list');
    if (lessonsList) {
      lessonsList.innerHTML = '';
      if (data.lessons && data.lessons.length > 0) {
        data.lessons.forEach(lesson => {
          const item = document.createElement('div');
          item.className = 'rule-item';
          item.style.padding = "0.6rem 0.8rem";
          item.style.background = "rgba(255, 255, 255, 0.02)";
          item.style.borderRadius = "8px";
          item.style.borderLeft = "3px solid var(--accent-warning)";
          item.style.marginBottom = "0.5rem";
          item.style.fontSize = "0.85rem";
          item.textContent = lesson;
          lessonsList.appendChild(item);
        });
      } else {
        lessonsList.innerHTML = '<p class="text-muted" style="font-size: 0.85rem;">No lessons learned recorded yet.</p>';
      }
    }

    // 8. Synthesized Rules
    const rulesList = document.getElementById('rules-list');
    if (rulesList) {
      rulesList.innerHTML = '';
      if (data.rules && data.rules.length > 0) {
        data.rules.forEach(rule => {
          const item = document.createElement('div');
          item.className = 'rule-item';
          item.style.padding = "0.6rem 0.8rem";
          item.style.background = "rgba(255, 255, 255, 0.02)";
          item.style.borderRadius = "8px";
          item.style.borderLeft = "3px solid var(--accent-primary)";
          item.style.marginBottom = "0.5rem";
          item.style.fontSize = "0.85rem";
          item.textContent = rule;
          rulesList.appendChild(item);
        });
      } else {
        rulesList.innerHTML = '<p class="text-muted" style="font-size: 0.85rem;">No synthesized rules recorded yet.</p>';
      }
    }

    // 9. SemVer Releases
    const changelogList = document.getElementById('changelog-list');
    if (changelogList) {
      changelogList.innerHTML = '';
      if (data.changelog && data.changelog.length > 0) {
        data.changelog.forEach(release => {
          const item = document.createElement('div');
          item.className = 'changelog-row';
          item.innerHTML = `
            <span class="changelog-v">v${release.version}</span>
            <span class="text-muted" style="font-size: 0.8rem;">${release.date}</span>
          `;
          changelogList.appendChild(item);
        });
      } else {
        changelogList.innerHTML = '<p class="text-muted" style="font-size: 0.85rem;">No release history found.</p>';
      }
    }

    // 10. Token Budget rendering
    if (data.token_budget) {
      const budget = data.token_budget;
      const dailyUsed = budget.daily_used || 0;
      const dailyLimit = budget.daily_limit || 500000;
      const dailyPct = dailyLimit > 0 ? (dailyUsed / dailyLimit * 100) : 0;
      
      const monthlyUsed = budget.monthly_used || 0;
      const monthlyLimit = budget.monthly_limit || 5000000;
      const monthlyPct = monthlyLimit > 0 ? (monthlyUsed / monthlyLimit * 100) : 0;
      
      // Daily progress
      const dailyProgress = document.getElementById('token-daily-progress');
      if (dailyProgress) {
        dailyProgress.style.width = Math.min(dailyPct, 100) + '%';
        if (dailyPct > 90) dailyProgress.style.backgroundColor = 'var(--accent-error)';
        else if (dailyPct > 70) dailyProgress.style.backgroundColor = 'var(--accent-warning)';
        else dailyProgress.style.backgroundColor = 'var(--accent-success)';
      }
      const dailyLabel = document.getElementById('token-daily-label');
      if (dailyLabel) {
        dailyLabel.textContent = `${dailyUsed.toLocaleString()} / ${dailyLimit.toLocaleString()} tokens (${dailyPct.toFixed(2)}% utilized)`;
      }

      // Monthly progress
      const monthlyProgress = document.getElementById('token-monthly-progress');
      if (monthlyProgress) {
        monthlyProgress.style.width = Math.min(monthlyPct, 100) + '%';
        if (monthlyPct > 90) monthlyProgress.style.backgroundColor = 'var(--accent-error)';
        else if (monthlyPct > 70) monthlyProgress.style.backgroundColor = 'var(--accent-warning)';
        else monthlyProgress.style.backgroundColor = 'var(--accent-success)';
      }
      const monthlyLabel = document.getElementById('token-monthly-label');
      if (monthlyLabel) {
        monthlyLabel.textContent = `${monthlyUsed.toLocaleString()} / ${monthlyLimit.toLocaleString()} tokens (${monthlyPct.toFixed(2)}% utilized)`;
      }

      // Account breakdown list
      const accountsList = document.getElementById('token-accounts-list');
      if (accountsList) {
        accountsList.innerHTML = '';
        const accounts = budget.accounts || {};
        if (Object.keys(accounts).length > 0) {
          for (const [name, info] of Object.entries(accounts)) {
            const item = document.createElement('div');
            item.className = 'lock-card-row';
            item.style.padding = "0.6rem 0.8rem";
            item.style.background = "rgba(255, 255, 255, 0.02)";
            item.style.borderRadius = "8px";
            item.style.marginBottom = "0.5rem";
            item.innerHTML = `
              <div class="lock-info-box">
                <span class="module-name" style="color: var(--accent-primary); font-weight: 600;">🔑 ${name}</span>
                <span class="holder-branch" style="margin-top: 0.3rem;">
                  Daily: <code>${(info.daily_used || 0).toLocaleString()}</code> | 
                  Monthly: <code>${(info.monthly_used || 0).toLocaleString()}</code> | 
                  Total: <code>${(info.total_used || 0).toLocaleString()}</code>
                </span>
              </div>
            `;
            accountsList.appendChild(item);
          }
        } else {
          accountsList.innerHTML = '<p class="text-muted" style="font-size: 0.85rem;">No active API account usage logged.</p>';
        }
      }

      // Task breakdown list
      const tasksList = document.getElementById('token-tasks-list');
      if (tasksList) {
        tasksList.innerHTML = '';
        const tasks = budget.tasks || {};
        if (Object.keys(tasks).length > 0) {
          // Sort by updated_at desc
          const sortedTasks = Object.entries(tasks).sort((a, b) => {
            const aTime = a[1].updated_at || '';
            const bTime = b[1].updated_at || '';
            return bTime.localeCompare(aTime);
          });
          sortedTasks.forEach(([tId, info]) => {
            const item = document.createElement('div');
            item.className = 'git-status-item';
            item.style.padding = "0.6rem 0.8rem";
            item.style.background = "rgba(255, 255, 255, 0.02)";
            item.style.borderRadius = "8px";
            item.style.marginBottom = "0.5rem";
            item.style.borderLeft = "3px solid var(--accent-primary)";
            item.innerHTML = `
              <div style="display: flex; justify-content: space-between; width: 100%; font-size: 0.85rem;">
                <span style="font-weight: 600; color: var(--accent-light);">🎫 Task: ${tId}</span>
                <span class="text-muted">${info.updated_at ? new Date(info.updated_at).toLocaleString() : 'unknown'}</span>
              </div>
              <div style="margin-top: 0.3rem; font-size: 0.8rem; color: var(--text-secondary);">
                Total: <code>${(info.total_tokens || 0).toLocaleString()}</code> tokens 
                (<span style="color: var(--accent-warning);">${(info.prompt_tokens || 0).toLocaleString()}</span> prompt / 
                <span style="color: var(--accent-success);">${(info.completion_tokens || 0).toLocaleString()}</span> completion)
              </div>
            `;
            tasksList.appendChild(item);
          });
        } else {
          tasksList.innerHTML = '<p class="text-muted" style="font-size: 0.85rem;">No task token usage logged yet.</p>';
        }
      }
    }

  } catch (err) {
    console.error('Failed to load status:', err);
    refreshBtns.forEach(btn => {
      btn.disabled = false;
      btn.textContent = 'Refresh Audit';
    });
  }
};

let pollIntervalId = null;
let currentPollSpeed = 5000;

window.startPolling = function(speed) {
  if (pollIntervalId) {
    clearInterval(pollIntervalId);
  }
  currentPollSpeed = speed;
  pollIntervalId = setInterval(() => {
    if (document.visibilityState === 'visible') {
      window.loadData(false);
      window.loadProfiles();
    }
  }, speed);
};

// Auto run on load
document.addEventListener('DOMContentLoaded', () => {
  window.loadData(false);
  window.loadProfiles();
  window.startPolling(5000);
});

// Global function to sync project metadata and ADRs
window.syncWorkspace = async function() {
  const btn = document.getElementById('sync-btn');
  if (btn) {
    btn.disabled = true;
    btn.textContent = 'Syncing...';
  }
  try {
    const res = await fetch('/api/sync', { method: 'POST' });
    const result = await res.json();
    if (result.success) {
      window.loadData(true); // Re-run validation status to fetch new rules
      alert('Workspace synchronized successfully!');
    } else {
      alert('Sync failed: ' + (result.message || 'Unknown error'));
    }
  } catch (err) {
    console.error('Failed to sync workspace:', err);
    alert('Failed to sync workspace.');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = 'Sync Workspace';
    }
  }
};

// Global function to handle lock acquisition
window.handleAcquireLock = async function(event) {
  event.preventDefault();
  const input = document.getElementById('lock-module-input');
  const module = input.value.trim();
  if (!module) return;

  const btn = event.target.querySelector('button[type="submit"]');
  btn.disabled = true;
  btn.textContent = 'Locking...';

  try {
    const res = await fetch('/api/locks/acquire', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ module: module })
    });
    const result = await res.json();
    if (result.success) {
      input.value = '';
      window.loadData(true);
      alert(result.message || 'Lock acquired successfully!');
    } else {
      alert('Failed to acquire lock: ' + (result.message || 'Unknown error'));
    }
  } catch (err) {
    console.error('Failed to acquire lock:', err);
    alert('Failed to connect to server.');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Acquire Lock';
  }
};

// Global function to handle lock release
window.handleReleaseLock = async function(module) {
  if (!confirm(`Are you sure you want to release the lock on module "${module}"?`)) {
    return;
  }
  try {
    const res = await fetch('/api/locks/release', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ module: module })
    });
    const result = await res.json();
    if (result.success) {
      window.loadData(true);
    } else {
      alert('Failed to release lock: ' + (result.message || 'Unknown error'));
    }
  } catch (err) {
    console.error('Failed to release lock:', err);
  }
};

// Global function to handle lesson learned submission
window.handleRecordLesson = async function(event) {
  event.preventDefault();
  const category = document.getElementById('lesson-category').value.trim();
  const lesson = document.getElementById('lesson-content').value.trim();
  if (!lesson) return;

  const btn = event.target.querySelector('button[type="submit"]');
  btn.disabled = true;
  btn.textContent = 'Recording...';

  try {
    const res = await fetch('/api/learn', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lesson: lesson, category: category })
    });
    const result = await res.json();
    if (result.success) {
      document.getElementById('record-lesson-form').reset();
      window.loadData(true);
      alert('Lesson recorded and rules synchronized!');
    } else {
      alert('Failed to record lesson: ' + (result.message || 'Unknown error'));
    }
  } catch (err) {
    console.error('Failed to record lesson:', err);
    alert('Failed to connect to server.');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Record Lesson';
  }
};

// Global function to copy public key to clipboard
window.copyPublicKey = function() {
  const box = document.getElementById('pubkey-content');
  if (!box) return;
  navigator.clipboard.writeText(box.textContent).then(() => {
    const btn = document.getElementById('copy-pubkey-btn');
    if (btn) {
      const origText = btn.textContent;
      btn.textContent = 'Copied!';
      btn.style.background = 'var(--accent-success)';
      setTimeout(() => {
        btn.textContent = origText;
        btn.style.background = '';
      }, 2000);
    }
  });
};

// Global function to switch git profiles
window.handleSwitchProfile = async function(name) {
  try {
    const res = await fetch('/api/profiles/switch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: name })
    });
    const result = await res.json();
    if (result.success) {
      window.loadProfiles();
      window.loadData(true); // Force run validation status on profile switch
    } else {
      alert('Error switching profile: ' + (result.message || 'Unknown error'));
    }
  } catch (err) {
    console.error('Failed to switch profile:', err);
  }
};

// Global function to handle new profile creation
window.handleCreateProfile = async function(event) {
  event.preventDefault();
  const name = document.getElementById('prof-name').value.trim();
  const email = document.getElementById('prof-email').value.trim();
  const signingKey = document.getElementById('prof-gpg').value.trim() || null;
  const sshKeyPath = document.getElementById('prof-ssh-path').value.trim() || null;
  const gitToken = document.getElementById('prof-token').value.trim() || null;
  const generateSsh = document.getElementById('prof-gen-ssh').checked;
  const switchAfter = document.getElementById('prof-switch-after').checked;

  const btn = event.target.querySelector('button[type="submit"]');
  btn.disabled = true;
  btn.textContent = 'Registering...';

  try {
    const res = await fetch('/api/profiles/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: name,
        email: email,
        signing_key: signingKey,
        ssh_key_path: sshKeyPath,
        git_token: gitToken,
        generate_ssh: generateSsh,
        switch_after: switchAfter
      })
    });
    const result = await res.json();
    if (result.success) {
      document.getElementById('create-profile-form').reset();
      window.loadProfiles();
      window.loadData(true);
      alert('Profile registered successfully!');
    } else {
      alert('Error registering profile: ' + (result.message || 'Unknown error'));
    }
  } catch (err) {
    console.error('Failed to create profile:', err);
    alert('Failed to connect to the server.');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Create Profile';
  }
};

// Load Git profiles list and active details
window.loadProfiles = async function() {
  try {
    const res = await fetch('/api/profiles');
    if (!res.ok) return;
    const data = await res.json();
    const profiles = data.profiles || [];
    
    // Find active profile
    const active = profiles.find(p => p.active);
    
    // 1. Render Active Profile Details Card
    const detailsContainer = document.getElementById('active-profile-details');
    if (detailsContainer) {
      if (active) {
        let keyRowHtml = '';
        if (active.ssh_key_path) {
          keyRowHtml = `
            <div class="label">SSH Key Path:</div>
            <div class="val">${active.ssh_key_path}</div>
          `;
        } else if (active.signing_key) {
          keyRowHtml = `
            <div class="label">Signing Key:</div>
            <div class="val">${active.signing_key}</div>
          `;
        }
        
        detailsContainer.innerHTML = `
          <div class="profile-details-table">
            <div class="label">Name:</div>
            <div class="val">${active.name}</div>
            <div class="label">Email:</div>
            <div class="val">${active.email}</div>
            ${keyRowHtml}
            <div class="label">GitHub PAT:</div>
            <div class="val">${active.git_token ? '•••••••••••• (Configured)' : 'None'}</div>
          </div>
          <div id="ssh-pubkey-display" style="display:none;"></div>
        `;
        
        // If profile has SSH key path, fetch and display public key
        if (active.ssh_key_path) {
          try {
            const pubRes = await fetch(`/api/ssh/public-key?profile=${encodeURIComponent(active.name)}`);
            if (pubRes.ok) {
              const pubData = await pubRes.json();
              if (pubData.public_key) {
                const pubDisplay = document.getElementById('ssh-pubkey-display');
                if (pubDisplay) {
                  pubDisplay.style.display = 'block';
                  pubDisplay.innerHTML = `
                    <div class="pubkey-container">
                      <div class="pubkey-header">
                        <h3>🔑 Ed25519 Public Key</h3>
                        <button class="btn-secondary" id="copy-pubkey-btn" onclick="window.copyPublicKey()">Copy Key</button>
                      </div>
                      <div class="pubkey-box" id="pubkey-content">${pubData.public_key}</div>
                    </div>
                  `;
                }
              }
            }
          } catch (pubErr) {
            console.error('Failed to load public key:', pubErr);
          }
        }
      } else {
        detailsContainer.innerHTML = `
          <p class="text-muted" style="font-size:0.85rem; margin:0;">
            No active Git profile set up. Use the form to register one.
          </p>
        `;
      }
    }
    
    // 2. Render Registered Profiles List
    const listContainer = document.getElementById('profiles-list-container');
    if (listContainer) {
      listContainer.innerHTML = '';
      if (profiles.length > 0) {
        profiles.forEach(p => {
          const isCurrent = p.active;
          const card = document.createElement('div');
          card.className = 'profile-card' + (isCurrent ? ' active' : '');
          
          let actionHtml = '';
          if (isCurrent) {
            actionHtml = `<span class="status-badge pass" style="font-size:0.7rem; font-weight:600;">ACTIVE</span>`;
          } else {
            actionHtml = `<button class="btn-secondary" onclick="window.handleSwitchProfile('${p.name}')">Switch</button>`;
          }
          
          card.innerHTML = `
            <div class="profile-info">
              <span class="name">${p.name}</span>
              <span class="email">${p.email}</span>
            </div>
            <div class="profile-action">
              ${actionHtml}
            </div>
          `;
          listContainer.appendChild(card);
        });
      } else {
        listContainer.innerHTML = '<p class="text-muted" style="font-size: 0.85rem; margin:0;">No registered profiles found.</p>';
      }
    }
    
  } catch (err) {
    console.error('Failed to load profiles:', err);
  }
};
