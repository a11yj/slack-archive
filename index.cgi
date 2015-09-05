#!/usr/local/bin/perl

use strict;
use utf8;
use CGI;
use Storable;
use Cwd;
use YAML::Tiny;
use Encode 'encode';

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
  if ( -f "$datadir/ch_$_->{name}" ) {
		push @channels, $_;
}
}

  print "<ul>\n";
  foreach (@channels) {
    my $ch= $_->{name};
    my ($sec, $min, $hr, $day, $mon, $year) = localtime($_->{updated});
    $year += 1900;
    $mon++;
    my $updated = "$year-$mon-$day $hr:$min:$sec";

    print "<li><a href=\"$url?channel=$ch\">#$ch ($updated 更新)</a></li>\n";
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

my $chinfo;
if ( -f $channelfile ) {
$chinfo = retrieve("$channelfile");
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
my $linked_channel_id;

    $text =~ s/</&lt;/g;
    $text =~ s/>/&gt;/g;
    $text =~ s/\n/<br>/g;

    while ( $text =~ m/&lt;\@(U.+?)&gt;/ ) {
      $mention_uid = $1;
      my $mention_name = $mention_uid;
      if ( exists($users->{$mention_uid}) ) {
    	$mention_name = $users->{$mention_uid};
      }
      $text =~ s/&lt;\@$mention_uid&gt;/\@$mention_name/;
    }
    
    while ( $text =~ m/&lt;#(C.+?)&gt;/ ) {
      $linked_channel_id = $1;
      my $linked_channel_name = $linked_channel_id;
      foreach (@$chinfo) {
    	if ( $_->{id} eq $linked_channel_id ) {
	  $linked_channel_name = $_->{name};
	}
      }
  	
      $text =~ s/&lt;#$linked_channel_id&gt;/#$linked_channel_name/;
    }

    while ( $text =~ m|&lt;(https?://.+?)&gt;| ) {
my $linked_url = $1;
  	
	$text =~ s|&lt;$linked_url&gt;|<a href="$linked_url">$linked_url</a>|;
    }
        
    print "<li>$msg->{user}: " . encode('UTF-8', $text);
    my ($sec, $min, $hr, $day, $mon, $year) = localtime($msg->{time});
    $year += 1900;
    $mon++;
    print "<br>($year/$mon/$day $hr:$min:$sec)</li>\n";
  }
  print '</ul><p><a href="/">アーカイブ・リストに戻る</a> - <a href="https://a11yj.herokuapp.com/">このSlack Teamに参加する</a></p></body></html>';

}

