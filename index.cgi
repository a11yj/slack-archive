#!/usr/local/bin/perl

use strict;
use utf8;
use CGI;
use Storable;
use Cwd;
use YAML::Tiny;

my $basedir = getcwd;
my $datadir = "$basedir/data";
my $ConfigFile = "$datadir/slack-archive.conf";
my $userfile = "$datadir/users";
my $channelfile = "$datadir/channels";
my $url = "http://a11yj.ma10.jp/";

if ( -f $ConfigFile ) {
  my $config = YAML::Tiny->read("$ConfigFile");
  $url = $config->[0]->{url};
}

my $obj = new CGI;

my $channel = $obj->param('channel');
my $action = 'list';

if ( $channel ne '' ) {
  $action = 'show';
}
print $obj->header(-type => 'text/html;charset=utf-8');


if ( $action eq 'list' ) {
  &list;
} elsif ( $action eq 'show' ) {
  &show($channel);
}

exit;

sub list {
  binmode(STDOUT, ":utf8");
  print << "EOM";
<!DOCTYPE html>
<head>
<title>A11YJ.slack.com チャンネル・アーカイブ</title>
</head>
<body>
<h1>A11YJ.slack.com チャンネル・アーカイブ</h1>
<p>以下のチャンネルのアーカイブを提供しています。</p>
EOM

my $chinfo;
if ( -f $channelfile ) {
$chinfo = retrieve("$channelfile");
}

my @channels;
foreach (@$chinfo) {
	if ( -f "$datadir/ch_$_->{name} ) {
		push @channels, $_;
}
}

  print "<ul>\n";
  foreach (@channels) {
my $ch= $_->{name};
my $updated = $_->{updated};

    print "<li><a href=\"$url?channel=$ch\">#$ch ($updated)</a></li>\n";
  }
  print '</ul><p><a href="https://a11yj.herokuapp.com/">このSlack Teamに参加する</a></p></body></html>';

  return 1;
}

sub show {
  my $channel = shift;

  my $data = retrieve("$datadir/ch_$channel");
  my $users = {};
  if ( -f $userfile ) {
    $users = retrieve("$userfile");
  }
  
  print << "EOM";
<!DOCTYPE html>
<head>
<title>#$channel on A11YJ.slack.com チャンネル・アーカイブ</title>
</head>
<body>
<h1>#$channel on a11yj.slack.com チャンネル・アーカイブ</h1>
<ul>
EOM

  foreach my $msg (@$data) {
    my $text = $msg->{text};
    my $mention_uid = "";
    $text =~ m/<@([^>]+)>/;
    $mention_uid = $1 if ( defined($1) );
    if ( $mention_uid ne '' ) {
      my $mention_name = $mention_uid;
      if ( exists($users->{$mention_uid}) ) {
	$mention_name = $users->{$mention_uid};
      }
      $text =~ s/<\@$mention_uid>/\@$mention_name/;
    }
			     
    $text =~ s/</&lt;/g;
    $text =~ s/>/&gt;/g;
    $text =~ s/\n/<br>/g;
    print "<li>$msg->{user}: $text";
    my ($sec, $min, $hr, $day, $mon, $year) = localtime($msg->{time});
    $year += 1900;
    $mon++;
    print "<br>($year/$mon/$day $hr:$min:$sec)</li>\n";
  }
  print '</ul><p><a href="/">アーカイブ・リストに戻る</a> - <a href="https://a11yj.herokuapp.com/">このSlack Teamに参加する</a></p></body></html>';

}

